"""
Pydantic request / response models for the auth API.

Strict validation rules enforced here:
  * email must be a valid Gmail address (ends with @gmail.com)
  * password must satisfy a strong-password policy
  * role at signup is restricted to {user, sos, depanage} — admin is forbidden
  * phone must be a valid international number (E.164)
  * OTP code must be exactly 6 digits
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Literal, Optional

import phonenumbers
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.user import UserRole

# ─── Constants ───────────────────────────────────────────────────────────────

_PASSWORD_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]).{8,}$"
)
_GMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@gmail\.com$")
_OTP_RE = re.compile(r"^\d{6}$")

SignupRole = Literal["user", "sos", "depanage"]


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _validate_gmail(value: str) -> str:
    """Lowercase + enforce @gmail.com suffix."""
    v = value.strip().lower()
    if not _GMAIL_RE.match(v):
        raise ValueError("Email must be a valid Gmail address (ends with @gmail.com).")
    return v


def _validate_password(value: str) -> str:
    if not _PASSWORD_RE.match(value):
        raise ValueError(
            "Password must be at least 8 characters and include an uppercase "
            "letter, a lowercase letter, a digit, and a special character."
        )
    return value


# ─── Signup ──────────────────────────────────────────────────────────────────


class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=120, examples=["Jane Doe"])
    email: EmailStr = Field(..., examples=["jane@gmail.com"])
    phone: str = Field(..., examples=["+213555123456"])
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    # `role` defaults to "user". Public clients CANNOT request "admin" — that's
    # a Literal-restricted field; pydantic will 422 the request.
    role: SignupRole = Field(default="user", examples=["user", "sos", "depanage"])

    @field_validator("full_name")
    @classmethod
    def sanitize_full_name(cls, v: str) -> str:
        cleaned = " ".join(v.strip().split())
        if not re.match(r"^[\w\s\-'.]+$", cleaned):
            raise ValueError("Full name contains invalid characters.")
        return cleaned

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return _validate_gmail(v)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError
        except Exception:
            raise ValueError(
                "Invalid phone number. Use international format, e.g. +213555123456"
            )
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return _validate_password(v)

    @model_validator(mode="after")
    def passwords_match(self) -> "SignupRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


# ─── OTP ─────────────────────────────────────────────────────────────────────


class OtpVerifyRequest(BaseModel):
    """Used by /auth/verify-email — signup-time email verification."""
    email: EmailStr = Field(..., examples=["jane@gmail.com"])
    code: str = Field(..., min_length=6, max_length=6, examples=["123456"])

    @field_validator("email")
    @classmethod
    def must_be_gmail(cls, v: str) -> str:
        return _validate_gmail(v)

    @field_validator("code")
    @classmethod
    def code_is_6_digits(cls, v: str) -> str:
        if not _OTP_RE.match(v):
            raise ValueError("Code must be exactly 6 digits.")
        return v


class ResendOtpRequest(BaseModel):
    """Used by /auth/resend-otp — for either signup or login OTP."""
    email: EmailStr = Field(..., examples=["jane@gmail.com"])
    purpose: Literal["signup", "login"] = Field(default="signup")

    @field_validator("email")
    @classmethod
    def must_be_gmail(cls, v: str) -> str:
        return _validate_gmail(v)


class VerifyLoginOtpRequest(BaseModel):
    """
    Used by /auth/verify-login-otp.

    The client must send back the short-lived ``pre_auth_token`` it received
    from POST /auth/login, together with the 6-digit OTP that arrived via email.
    """
    pre_auth_token: str = Field(..., min_length=10)
    code: str = Field(..., min_length=6, max_length=6, examples=["123456"])

    @field_validator("code")
    @classmethod
    def code_is_6_digits(cls, v: str) -> str:
        if not _OTP_RE.match(v):
            raise ValueError("Code must be exactly 6 digits.")
        return v


# ─── Login ───────────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["jane@gmail.com"])
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def must_be_gmail(cls, v: str) -> str:
        return _validate_gmail(v)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10)


# ─── Responses ───────────────────────────────────────────────────────────────


class UserPublic(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    role: UserRole
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True, "use_enum_values": True}


class MessageResponse(BaseModel):
    message: str


class OtpSentResponse(BaseModel):
    """Returned by /auth/signup and /auth/resend-otp."""
    message: str
    email: str
    expires_in_minutes: int
    resend_in_seconds: int


class PreAuthTokenResponse(BaseModel):
    """Returned by /auth/login after password verification (step 1 of 2)."""
    message: str
    pre_auth_token: str
    expires_in_minutes: int
    next_step: Literal["verify-login-otp"] = "verify-login-otp"


class TokenResponse(BaseModel):
    """Returned by /auth/verify-login-otp (full session) and /auth/refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserPublic


# ─── Admin RBAC ─────────────────────────────────────────────────────────────


class UpdateUserRoleRequest(BaseModel):
    """Admin-only: change another user's role (including granting admin)."""
    role: UserRole

    @field_validator("role")
    @classmethod
    def role_is_known(cls, v: UserRole) -> UserRole:
        return v
