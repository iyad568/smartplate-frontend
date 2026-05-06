import logging
import sys
from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    level = logging.DEBUG if not settings.is_production else logging.INFO
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # `force=True` is critical: uvicorn installs root handlers before our
    # lifespan / module-level setup_logging() runs, which makes plain
    # basicConfig() a no-op and silences every logger.info(...) call.
    logging.basicConfig(
        level=level,
        format=fmt,
        datefmt=datefmt,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Make sure our own app loggers actually emit at INFO/DEBUG, regardless
    # of what uvicorn's defaults set the root logger to.
    logging.getLogger("app").setLevel(level)

    # Quieten noisy libs in production
    if settings.is_production:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("asyncpg").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
