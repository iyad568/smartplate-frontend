from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.db.session import create_tables

# Import models so SQLAlchemy registers them on Base.metadata before
# create_tables / Alembic autogenerate runs.
import app.models.user            # noqa: F401
import app.models.otp_code        # noqa: F401
import app.models.sos_request     # noqa: F401
import app.models.depannage_request  # noqa: F401
import app.models.car             # noqa: F401

setup_logging()
logger = get_logger(__name__)
settings = get_settings()


# ─── Lifespan ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SmartPlate API [%s]", settings.APP_ENV)
    if not settings.is_production:
        await create_tables()  # Production should run `alembic upgrade head`
    yield
    logger.info("Shutting down SmartPlate API")


# ─── App factory ──────────────────────────────────────────────────────────────


limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="SmartPlate Auth API",
    description="Email + OTP authentication with role-based access control.",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# ─── Rate limiting ────────────────────────────────────────────────────────────

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] if settings.is_production else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ─── Global exception handlers ────────────────────────────────────────────────


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Always log full traceback to the server console.
    logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    # In development, surface the real error type + message so you don't
    # have to grep server logs. Production keeps the response opaque.
    detail = (
        f"{type(exc).__name__}: {exc}"
        if not settings.is_production
        else "Internal server error."
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )


# ─── Request logging middleware ───────────────────────────────────────────────


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("→ %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("← %s %s %s", request.method, request.url.path, response.status_code)
    return response


# ─── Static file serving (uploaded documents) ─────────────────────────────────

UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


# ─── Routes ───────────────────────────────────────────────────────────────────


app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "env": settings.APP_ENV}
