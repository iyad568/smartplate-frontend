"""
OTP codes table.

Stores one-time-password codes used for:
  - signup email verification    (purpose = "signup")
  - login second factor          (purpose = "login")

The code is stored *hashed* (bcrypt), never in plaintext, so a DB leak does
not expose live OTPs.
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Index, func,
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class OtpPurpose(str, enum.Enum):
    SIGNUP = "signup"   # email verification on registration
    LOGIN = "login"     # second-factor on login
    PASSWORD = "password"  # password change verification


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Hashed OTP — bcrypt of the plaintext 6-digit code.
    code: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[OtpPurpose] = mapped_column(
        SAEnum(OtpPurpose, name="otp_purpose", native_enum=True),
        nullable=False,
        default=OtpPurpose.SIGNUP,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("User", lazy="joined")

    __table_args__ = (
        # Find latest unused active OTP for a user+purpose quickly.
        Index("ix_otp_user_purpose_used", "user_id", "purpose", "used"),
    )

    # ─── Helpers ──────────────────────────────────────────────────────────────

    @property
    def is_expired(self) -> bool:
        # Compare in UTC; expires_at is timezone-aware.
        return datetime.now(timezone.utc) >= self.expires_at

    @property
    def is_active(self) -> bool:
        return (not self.used) and (not self.is_expired)

    def __repr__(self) -> str:
        return (
            f"<OtpCode user_id={self.user_id} purpose={self.purpose.value} "
            f"used={self.used} expires_at={self.expires_at.isoformat()}>"
        )
