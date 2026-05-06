"""
OTP issuance / verification service.

Single entrypoint for everything OTP:
  * issue_otp()    — generate, hash, store, email a fresh OTP (handles resend cooldown)
  * verify_otp()   — constant-time match, expiry + single-use enforcement
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import generate_numeric_otp, hash_otp, verify_otp as _verify_otp_hash
from app.db.repositories.otp_repo import OtpRepository
from app.models.otp_code import OtpCode, OtpPurpose
from app.models.user import User
from app.services.email_service import send_login_otp_email, send_signup_otp_email

settings = get_settings()
logger = get_logger(__name__)


class OtpService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OtpRepository(db)

    # ─── Issue ──────────────────────────────────────────────────────────────

    async def issue_otp(
        self,
        *,
        user: User,
        purpose: OtpPurpose,
        enforce_cooldown: bool = True,
    ) -> OtpCode:
        """
        Generate a new OTP, store it (hashed), email it.

        Invalidates any prior active OTPs for the same (user, purpose) so only
        the newest code is ever valid.
        """
        if enforce_cooldown:
            self._enforce_cooldown_or_raise(
                await self.repo.latest_for_user(user_id=user.id, purpose=purpose)
            )

        # Invalidate any prior active codes for this user+purpose.
        await self.repo.invalidate_active_for_user(user_id=user.id, purpose=purpose)

        plain_code = generate_numeric_otp(settings.OTP_LENGTH)
        hashed = hash_otp(plain_code)

        otp = await self.repo.create(
            user_id=user.id,
            hashed_code=hashed,
            purpose=purpose,
            expires_minutes=settings.OTP_EXPIRE_MINUTES,
        )

        # Fire-and-await: failures are logged inside _send and don't raise.
        if purpose == OtpPurpose.SIGNUP:
            await send_signup_otp_email(to=user.email, full_name=user.full_name, code=plain_code)
        else:
            await send_login_otp_email(to=user.email, full_name=user.full_name, code=plain_code)

        logger.info(
            "Issued OTP user_id=%s purpose=%s expires_at=%s",
            user.id, purpose.value, otp.expires_at.isoformat(),
        )
        return otp

    # ─── Verify ─────────────────────────────────────────────────────────────

    async def verify_and_consume(
        self,
        *,
        user: User,
        purpose: OtpPurpose,
        plain_code: str,
    ) -> OtpCode:
        """Verify a 6-digit OTP for (user, purpose) and mark it used."""
        active = await self.repo.get_latest_active(user_id=user.id, purpose=purpose)
        if active is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active code. Please request a new one.",
            )

        if not _verify_otp_hash(plain_code, active.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired code.",
            )

        # Single-use: mark used immediately.
        return await self.repo.mark_used(active)

    # ─── Helpers ────────────────────────────────────────────────────────────

    def _enforce_cooldown_or_raise(self, last: OtpCode | None) -> None:
        if last is None:
            return
        elapsed = (datetime.now(timezone.utc) - last.created_at).total_seconds()
        if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
            wait = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {wait} seconds before requesting another code.",
            )
