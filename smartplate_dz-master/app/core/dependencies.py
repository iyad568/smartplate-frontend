"""
FastAPI dependencies for authentication & role-based access control.

Usage:

    from app.core.dependencies import get_current_user, require_roles
    from app.models.user import UserRole

    @router.get("/admin/users", dependencies=[Depends(require_roles(UserRole.ADMIN))])
    async def list_users(...):
        ...

    @router.get("/me")
    async def me(user: User = Depends(get_current_user)):
        return user

The ``otp_pending`` pre-auth token is intentionally rejected here so that an
attacker who has only completed step-1 of login cannot reach protected
resources.
"""
from __future__ import annotations

from typing import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.repositories.user_repo import UserRepository
from app.db.session import get_db
from app.models.user import User, UserRole

# `auto_error=True` returns 403 if the Authorization header is missing —
# we replace that below with an explicit 401 for consistency.
_bearer = HTTPBearer(auto_error=False)


_UNAUTHENTICATED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication required.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the request's bearer token to a verified User, or 401."""
    if credentials is None or not credentials.credentials:
        raise _UNAUTHENTICATED

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise _UNAUTHENTICATED

    if payload.get("type") != "access":
        # Pre-auth and refresh tokens cannot be used to authenticate API calls.
        raise _UNAUTHENTICATED

    user_id = payload.get("sub")
    if not user_id:
        raise _UNAUTHENTICATED

    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise _UNAUTHENTICATED

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified.",
        )

    return user


def require_roles(*roles: UserRole | str):
    """
    FastAPI dependency factory enforcing role-based authorization.

    Example::

        @router.get("/admin/users", dependencies=[Depends(require_roles(UserRole.ADMIN))])

    or with the user injected::

        @router.get("/sos/active")
        async def active(user: User = Depends(require_roles(UserRole.SOS, UserRole.ADMIN))):
            ...

    Admins implicitly bypass any role check (universal access).
    """
    allowed = {
        (r.value if isinstance(r, UserRole) else str(r)).lower()
        for r in roles
    }

    async def _checker(user: User = Depends(get_current_user)) -> User:
        user_role_value = (
            user.role.value if isinstance(user.role, UserRole) else str(user.role)
        ).lower()
        if user_role_value == UserRole.ADMIN.value or user_role_value in allowed:
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This endpoint requires one of these roles: {sorted(allowed)}.",
        )

    return _checker


# Convenience dependency: an explicit "admin only" gate.
require_admin = require_roles(UserRole.ADMIN)
