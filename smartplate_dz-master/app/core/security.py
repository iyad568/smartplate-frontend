"""
Cryptographic helpers: password hashing, OTP hashing, and JWT token issuance.

Token types issued by this service:
  * "access"        — short-lived bearer for protected API routes (carries role)
  * "refresh"       — long-lived rotation token
  * "otp_pending"   — short-lived single-purpose token issued AFTER the password
                      step of /auth/login. The client exchanges it (along with
                      the emailed OTP) at /auth/verify-login-otp for a real
                      access+refresh pair. It MUST NOT be accepted by any
                      protected route.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

# A single context handles both passwords and OTPs. ``bcrypt`` truncates
# inputs over 72 bytes, but a 6-digit OTP is far below that limit, so reuse
# is safe and avoids a second dependency.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Passwords ───────────────────────────────────────────────────────────────


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _pwd_context.verify(plain, hashed)
    except Exception:
        # Defensive: malformed hash, etc. — never raise to caller.
        return False


# ─── OTPs (hashed at rest) ───────────────────────────────────────────────────


def hash_otp(plain_code: str) -> str:
    return _pwd_context.hash(plain_code)


def verify_otp(plain_code: str, hashed: str) -> bool:
    try:
        return _pwd_context.verify(plain_code, hashed)
    except Exception:
        return False


def generate_numeric_otp(length: int | None = None) -> str:
    """Generate a cryptographically-secure n-digit OTP (default from settings)."""
    n = length or settings.OTP_LENGTH
    upper = 10**n
    code = secrets.randbelow(upper)
    return f"{code:0{n}d}"


# ─── JWT ─────────────────────────────────────────────────────────────────────

TokenKind = Literal["access", "refresh", "otp_pending"]


def _create_token(
    *,
    subject: str,
    kind: TokenKind,
    expire_delta: timedelta,
    extra: dict | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict = {
        "sub": subject,
        "type": kind,
        "iat": now,
        "exp": now + expire_delta,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(*, user_id: str, email: str, role: str) -> str:
    return _create_token(
        subject=user_id,
        kind="access",
        expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra={"email": email, "role": role},
    )


def create_refresh_token(*, user_id: str) -> str:
    return _create_token(
        subject=user_id,
        kind="refresh",
        expire_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_pre_auth_token(*, user_id: str) -> str:
    """Short-lived token tying the second login step (OTP) to the first (password)."""
    return _create_token(
        subject=user_id,
        kind="otp_pending",
        expire_delta=timedelta(minutes=settings.PRE_AUTH_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str) -> dict:
    """Decode and validate a JWT. Raises jose.JWTError on failure."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# ─── URL-safe random tokens (general-purpose) ────────────────────────────────


def generate_secure_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)
