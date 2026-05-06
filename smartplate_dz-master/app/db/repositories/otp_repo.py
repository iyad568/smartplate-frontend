"""
Repository for the ``otp_codes`` table.

Stores OTPs hashed (never plaintext). Provides:
  - create()                       — store a freshly generated OTP for a user/purpose
  - get_latest_active()            — newest unused, unexpired OTP for a user/purpose
  - mark_used()                    — single-use enforcement
  - invalidate_active_for_user()   — invalidate prior pending codes when a new one is issued
  - delete_expired()               — housekeeping
  - latest_for_user()              — for resend cooldown
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.otp_code import OtpCode, OtpPurpose

logger = get_logger(__name__)


class OtpRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        user_id: str,
        hashed_code: str,
        purpose: OtpPurpose,
        expires_minutes: int,
    ) -> OtpCode:
        """Insert a new OTP. Caller is expected to have invalidated previous active codes."""
        otp = OtpCode(
            user_id=user_id,
            code=hashed_code,
            purpose=purpose,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
            used=False,
        )
        self.db.add(otp)
        await self.db.flush()
        await self.db.refresh(otp)
        return otp

    async def invalidate_active_for_user(
        self, *, user_id: str, purpose: OtpPurpose
    ) -> int:
        """
        Mark all currently-active OTPs for (user, purpose) as used.

        Called before issuing a fresh code so an attacker who somehow obtained
        an old OTP can't replay it after a resend.
        Returns number of rows updated.
        """
        stmt = (
            update(OtpCode)
            .where(
                and_(
                    OtpCode.user_id == user_id,
                    OtpCode.purpose == purpose,
                    OtpCode.used.is_(False),
                )
            )
            .values(used=True)
        )
        result = await self.db.execute(stmt)
        return result.rowcount or 0

    async def get_latest_active(
        self, *, user_id: str, purpose: OtpPurpose
    ) -> OtpCode | None:
        """Return the newest *active* (unused, unexpired) OTP for (user, purpose)."""
        stmt = (
            select(OtpCode)
            .where(
                and_(
                    OtpCode.user_id == user_id,
                    OtpCode.purpose == purpose,
                    OtpCode.used.is_(False),
                    OtpCode.expires_at > datetime.now(timezone.utc),
                )
            )
            .order_by(OtpCode.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def latest_for_user(
        self, *, user_id: str, purpose: OtpPurpose
    ) -> OtpCode | None:
        """Return the most recently *issued* OTP regardless of state — used for resend cooldown."""
        stmt = (
            select(OtpCode)
            .where(
                and_(
                    OtpCode.user_id == user_id,
                    OtpCode.purpose == purpose,
                )
            )
            .order_by(OtpCode.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_used(self, otp: OtpCode) -> OtpCode:
        otp.used = True
        await self.db.flush()
        await self.db.refresh(otp)
        return otp

    async def delete_expired(self) -> int:
        stmt = delete(OtpCode).where(OtpCode.expires_at < datetime.now(timezone.utc))
        result = await self.db.execute(stmt)
        return result.rowcount or 0
