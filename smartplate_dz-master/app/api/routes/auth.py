"""
/auth/* endpoints — signup + email-OTP verification + 2-step login + resend.
"""
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.dependencies import get_current_user
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    OtpSentResponse,
    OtpVerifyRequest,
    PreAuthTokenResponse,
    RefreshTokenRequest,
    ResendOtpRequest,
    SignupRequest,
    TokenResponse,
    UserPublic,
    VerifyLoginOtpRequest,
)
from app.services.auth_service import AuthService

settings = get_settings()
logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


# ─── Signup ─────────────────────────────────────────────────────────────────


@router.post(
    "/signup",
    response_model=OtpSentResponse,
    status_code=201,
    summary="Register a new user (sends signup OTP)",
    responses={
        201: {"description": "Account created — OTP emailed"},
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("5/minute")
async def signup(
    request: Request,
    payload: SignupRequest,
    db: AsyncSession = Depends(get_db),
) -> OtpSentResponse:
    return await AuthService(db).signup(payload)


# ─── Verify signup email ────────────────────────────────────────────────────


@router.post(
    "/verify-email",
    response_model=TokenResponse,
    summary="Verify signup OTP and activate the account",
    responses={
        200: {"description": "Email verified — session issued"},
        400: {"description": "Invalid or expired OTP"},
        404: {"description": "Account not found"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("10/minute")
async def verify_email(
    request: Request,
    payload: OtpVerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await AuthService(db).verify_email(payload)


# ─── Login (step 1: password) ───────────────────────────────────────────────


@router.post(
    "/login",
    response_model=PreAuthTokenResponse,
    summary="Authenticate password & email an OTP (step 1 of 2)",
    responses={
        200: {"description": "Password verified — OTP emailed"},
        401: {"description": "Invalid credentials"},
        403: {"description": "Email not verified"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(f"{get_settings().MAX_LOGIN_ATTEMPTS_PER_MINUTE}/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> PreAuthTokenResponse:
    return await AuthService(db).login(payload)


# ─── Login (step 2: OTP) ────────────────────────────────────────────────────


@router.post(
    "/verify-login-otp",
    response_model=TokenResponse,
    summary="Exchange pre-auth token + OTP for an access/refresh pair",
    responses={
        200: {"description": "Login complete — JWT pair issued"},
        400: {"description": "Invalid or expired OTP"},
        401: {"description": "Pre-auth token invalid/expired"},
    },
)
@limiter.limit("10/minute")
async def verify_login_otp(
    request: Request,
    payload: VerifyLoginOtpRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await AuthService(db).verify_login_otp(payload)


# ─── Resend OTP ─────────────────────────────────────────────────────────────


@router.post(
    "/resend-otp",
    response_model=OtpSentResponse,
    summary="Resend signup or login OTP (rate-limited)",
    responses={
        200: {"description": "If the account exists, a new code is sent"},
        400: {"description": "Wrong purpose for current account state"},
        429: {"description": "Cooldown not elapsed"},
    },
)
@limiter.limit("3/minute")
async def resend_otp(
    request: Request,
    payload: ResendOtpRequest,
    db: AsyncSession = Depends(get_db),
) -> OtpSentResponse:
    return await AuthService(db).resend_otp(payload)


# ─── Refresh + Me ───────────────────────────────────────────────────────────


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate access + refresh tokens",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await AuthService(db).refresh(payload)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Return the currently-authenticated user",
)
async def me(user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(user)
