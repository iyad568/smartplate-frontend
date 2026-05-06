"""
High-level auth orchestration.

Flows
=====
1. **Signup** (POST /auth/signup)
   - validate Gmail + role + strong password
   - hash password, save user with is_verified=False
   - issue signup OTP, email it, return ``OtpSentResponse``

2. **Verify email** (POST /auth/verify-email)
   - find user, consume signup OTP
   - flip is_verified=True

3. **Login step 1** (POST /auth/login)
   - verify password + email_verified
   - issue login OTP, email it
   - return short-lived ``pre_auth_token`` (otp_pending JWT)

4. **Login step 2** (POST /auth/verify-login-otp)
   - decode pre-auth token, consume login OTP
   - issue access + refresh JWTs (role embedded in access)

5. **Resend OTP** (POST /auth/resend-otp)
   - re-issue an active OTP, respecting cooldown
"""
from __future__ import annotations

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_pre_auth_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.repositories.user_repo import UserRepository
from app.models.otp_code import OtpPurpose
from app.models.user import SIGNUP_ALLOWED_ROLES, User, UserRole
from app.schemas.auth import (
    LoginRequest,
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
from app.services.otp_service import OtpService

settings = get_settings()
logger = get_logger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)
        self.otp = OtpService(db)

    # ─── Signup ─────────────────────────────────────────────────────────────

    async def signup(self, payload: SignupRequest) -> OtpSentResponse:
        # Belt-and-suspenders role guard. Pydantic's Literal already rejects
        # "admin" at the request layer; this enforces it server-side too.
        requested_role = payload.role
        if requested_role not in [role.value for role in SIGNUP_ALLOWED_ROLES]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot self-assign this role.",
            )

        if await self.users.email_exists(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered.",
            )

        user = await self.users.create(
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            hashed_password=hash_password(payload.password),
            role=requested_role,
        )
        logger.info("User signed up: id=%s email=%s role=%s", user.id, user.email, user.role)

        # Don't enforce cooldown on the first signup OTP.
        await self.otp.issue_otp(user=user, purpose=OtpPurpose.SIGNUP, enforce_cooldown=False)

        return OtpSentResponse(
            message="Account created. Check your email for the verification code.",
            email=user.email,
            expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
            resend_in_seconds=settings.OTP_RESEND_COOLDOWN_SECONDS,
        )

    # ─── Verify signup OTP ──────────────────────────────────────────────────

    async def verify_email(self, payload: OtpVerifyRequest) -> TokenResponse:
        user = await self.users.get_by_email(payload.email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account with that email.",
            )
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified.",
            )

        await self.otp.verify_and_consume(
            user=user, purpose=OtpPurpose.SIGNUP, plain_code=payload.code
        )
        await self.users.mark_verified(user)
        logger.info("Email verified: user_id=%s", user.id)

        return self._issue_session(user)

    # ─── Login step 1 (password) ───────────────────────────────────────────

    async def login(self, payload: LoginRequest) -> PreAuthTokenResponse:
        user = await self.users.get_by_email(payload.email)
        # Always do the password check (or a dummy one) to avoid user-enumeration
        # via response timing.
        if user is None or not verify_password(payload.password, user.hashed_password):
            logger.warning("Failed login for email=%s", payload.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before logging in.",
            )

        # Issue a fresh login OTP.
        await self.otp.issue_otp(user=user, purpose=OtpPurpose.LOGIN, enforce_cooldown=False)

        pre_auth = create_pre_auth_token(user_id=user.id)
        logger.info("Login step 1 ok: user_id=%s", user.id)

        return PreAuthTokenResponse(
            message="Password verified. Enter the code sent to your email.",
            pre_auth_token=pre_auth,
            expires_in_minutes=settings.PRE_AUTH_TOKEN_EXPIRE_MINUTES,
        )

    # ─── Login step 2 (OTP) ─────────────────────────────────────────────────

    async def verify_login_otp(self, payload: VerifyLoginOtpRequest) -> TokenResponse:
        try:
            data = decode_token(payload.pre_auth_token)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Pre-auth token is invalid or expired. Please log in again.",
            )

        if data.get("type") != "otp_pending":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong token type.",
            )

        user_id = data.get("sub")
        user = await self.users.get_by_id(user_id) if user_id else None
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
            )

        await self.otp.verify_and_consume(
            user=user, purpose=OtpPurpose.LOGIN, plain_code=payload.code
        )
        logger.info("Login step 2 ok: user_id=%s", user.id)

        return self._issue_session(user)

    # ─── Resend ────────────────────────────────────────────────────────────

    async def resend_otp(self, payload: ResendOtpRequest) -> OtpSentResponse:
        user = await self.users.get_by_email(payload.email)
        # Avoid leaking which emails exist.
        if user is None:
            return OtpSentResponse(
                message="If an account exists for that email, a new code has been sent.",
                email=payload.email,
                expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
                resend_in_seconds=settings.OTP_RESEND_COOLDOWN_SECONDS,
            )

        purpose = OtpPurpose.SIGNUP if payload.purpose == "signup" else OtpPurpose.LOGIN

        # Don't let an unverified user request login OTPs without going through signup first.
        if purpose == OtpPurpose.SIGNUP and user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified.",
            )
        if purpose == OtpPurpose.LOGIN and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verify your email before requesting a login code.",
            )

        await self.otp.issue_otp(user=user, purpose=purpose, enforce_cooldown=True)
        return OtpSentResponse(
            message="A new code has been sent.",
            email=user.email,
            expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
            resend_in_seconds=settings.OTP_RESEND_COOLDOWN_SECONDS,
        )

    # ─── Refresh ───────────────────────────────────────────────────────────

    async def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        try:
            data = decode_token(payload.refresh_token)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        if data.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong token type.",
            )

        user = await self.users.get_by_id(data.get("sub")) if data.get("sub") else None
        if user is None or not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        return self._issue_session(user)

    # ─── Password Change OTP ─────────────────────────────────────────────────────

    async def send_password_otp(self, user_id: str) -> OtpSentResponse:
        """Send OTP code for password change verification."""
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        # Issue password change OTP using the same email service as login
        try:
            await self.otp.issue_otp(user=user, purpose=OtpPurpose.PASSWORD, enforce_cooldown=True)
        except Exception as e:
            # Check if this is a database enum error
            if "otp_purpose" in str(e) and "PASSWORD" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database enum not updated. Please run: ALTER TYPE otp_purpose ADD VALUE 'PASSWORD';"
                )
            else:
                # Re-raise other unexpected errors
                raise
        
        return OtpSentResponse(
            message="Password change OTP sent to your email.",
            email=user.email,
            expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
            resend_in_seconds=settings.OTP_RESEND_COOLDOWN_SECONDS,
        )

    async def update_user_profile(self, user_id: str, update_data: dict) -> User:
        """Update user profile information."""
        # Import here to avoid circular imports
        from app.db.repositories.user_repo import UserRepository
        from app.core.security import hash_password
        
        user_repo = UserRepository(self.db)
        
        # Hash password if it's being updated (though we don't allow password updates here)
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        
        updated_user = await user_repo.update(user_id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password."""
        # Import here to avoid circular imports
        from app.db.repositories.user_repo import UserRepository
        from app.core.security import verify_password, hash_password
        
        user_repo = UserRepository(self.db)
        
        # Get user
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            return False
        
        # Validate new password
        if len(new_password) < 8:
            return False
        
        # Update password
        hashed_password = hash_password(new_password)
        updated_user = await user_repo.update_password(user, hashed_password)
        
        return updated_user is not None

    # ─── Internal ─────────────────────────────────────────────────────────--

    def _issue_session(self, user: User) -> TokenResponse:
        access = create_access_token(
            user_id=user.id, email=user.email, role=user.role
        )
        refresh = create_refresh_token(user_id=user.id)
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            user=UserPublic.model_validate(user),
        )
