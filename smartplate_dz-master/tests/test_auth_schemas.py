"""
Unit tests for auth Pydantic schemas.

These run without a database — they only validate request models.
Run with: pytest tests/ -v
"""
import pytest
from pydantic import ValidationError

from app.schemas.auth import (
    LoginRequest,
    OtpVerifyRequest,
    ResendOtpRequest,
    SignupRequest,
    VerifyLoginOtpRequest,
)


VALID_PAYLOAD = {
    "full_name": "Jane Doe",
    "email": "jane@gmail.com",
    "phone": "+213555123456",
    "password": "Secure@123",
    "confirm_password": "Secure@123",
    "role": "user",
}


def make(**overrides) -> dict:
    return {**VALID_PAYLOAD, **overrides}


# ─── Full name ───────────────────────────────────────────────────────────────


def test_valid_signup():
    req = SignupRequest(**VALID_PAYLOAD)
    assert req.full_name == "Jane Doe"
    assert req.role == "user"


def test_full_name_too_short():
    with pytest.raises(ValidationError, match="at least 3"):
        SignupRequest(**make(full_name="Jo"))


def test_full_name_invalid_chars():
    with pytest.raises(ValidationError):
        SignupRequest(**make(full_name="<script>alert(1)</script>"))


# ─── Email — Gmail only ─────────────────────────────────────────────────────


def test_non_gmail_rejected():
    with pytest.raises(ValidationError, match="Gmail"):
        SignupRequest(**make(email="jane@example.com"))


def test_gmail_normalized():
    req = SignupRequest(**make(email="Jane@GMAIL.com"))
    assert req.email == "jane@gmail.com"


def test_invalid_email():
    with pytest.raises(ValidationError):
        SignupRequest(**make(email="not-an-email"))


# ─── Phone ───────────────────────────────────────────────────────────────────


def test_invalid_phone():
    with pytest.raises(ValidationError, match="Invalid phone"):
        SignupRequest(**make(phone="0555123456"))   # missing country code


def test_phone_normalized():
    req = SignupRequest(**make(phone="+213 555 123 456"))
    assert req.phone == "+213555123456"


# ─── Password ───────────────────────────────────────────────────────────────


def test_weak_password_no_special_char():
    with pytest.raises(ValidationError):
        SignupRequest(**make(password="Secure123", confirm_password="Secure123"))


def test_weak_password_no_uppercase():
    with pytest.raises(ValidationError):
        SignupRequest(**make(password="secure@123", confirm_password="secure@123"))


def test_passwords_do_not_match():
    with pytest.raises(ValidationError, match="do not match"):
        SignupRequest(**make(confirm_password="Different@123"))


# ─── Role whitelist ─────────────────────────────────────────────────────────


def test_role_admin_rejected_at_signup():
    with pytest.raises(ValidationError):
        SignupRequest(**make(role="admin"))


def test_role_garbage_rejected():
    with pytest.raises(ValidationError):
        SignupRequest(**make(role="superuser"))


@pytest.mark.parametrize("role", ["user", "sos", "depanage"])
def test_signup_allowed_roles(role):
    req = SignupRequest(**make(role=role))
    assert req.role == role


def test_role_default_is_user():
    body = make()
    body.pop("role")
    req = SignupRequest(**body)
    assert req.role == "user"


# ─── OTP & login schemas ────────────────────────────────────────────────────


def test_otp_must_be_6_digits():
    with pytest.raises(ValidationError):
        OtpVerifyRequest(email="jane@gmail.com", code="12345")
    with pytest.raises(ValidationError):
        OtpVerifyRequest(email="jane@gmail.com", code="12345a")


def test_otp_verify_ok():
    req = OtpVerifyRequest(email="jane@gmail.com", code="123456")
    assert req.code == "123456"


def test_otp_verify_rejects_non_gmail():
    with pytest.raises(ValidationError, match="Gmail"):
        OtpVerifyRequest(email="jane@example.com", code="123456")


def test_login_rejects_non_gmail():
    with pytest.raises(ValidationError, match="Gmail"):
        LoginRequest(email="jane@example.com", password="Secure@123")


def test_login_ok():
    req = LoginRequest(email="JANE@gmail.com", password="Secure@123")
    assert req.email == "jane@gmail.com"


def test_resend_otp_purpose():
    req = ResendOtpRequest(email="jane@gmail.com", purpose="login")
    assert req.purpose == "login"


def test_resend_otp_rejects_bad_purpose():
    with pytest.raises(ValidationError):
        ResendOtpRequest(email="jane@gmail.com", purpose="reset")


def test_verify_login_otp_requires_both_fields():
    with pytest.raises(ValidationError):
        VerifyLoginOtpRequest(pre_auth_token="abc", code="123456")  # token too short
    with pytest.raises(ValidationError):
        VerifyLoginOtpRequest(pre_auth_token="x" * 20, code="abcdef")  # non-numeric code


def test_verify_login_otp_ok():
    req = VerifyLoginOtpRequest(pre_auth_token="x" * 20, code="123456")
    assert req.code == "123456"
