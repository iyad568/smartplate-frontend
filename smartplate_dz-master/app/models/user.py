import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class UserRole(str, enum.Enum):
    """
    Allowed application roles.

    NOTE: ``admin`` is intentionally NOT exposed to the public signup endpoint.
    It can only be set manually in the DB or by an existing admin via
    /admin/users/{id}/role.
    """
    USER = "user"
    SOS = "sos"
    DEPANAGE = "depanage"
    ADMIN = "admin"


# Roles a user can self-assign at signup.
SIGNUP_ALLOWED_ROLES: tuple[UserRole, ...] = (
    UserRole.USER,
    UserRole.SOS,
    UserRole.DEPANAGE,
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False,
        index=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    provider: Mapped[str] = mapped_column(
        String(50), default="email", nullable=False
    )
    google_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_picture: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    cars: Mapped[list["Car"]] = relationship("Car", back_populates="user", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} email={self.email} "
            f"role={self.role.value} verified={self.is_verified}>"
        )
