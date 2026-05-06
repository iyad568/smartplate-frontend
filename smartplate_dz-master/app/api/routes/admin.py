"""
Admin-only endpoints. Demonstrates the RBAC middleware.

All routes here are protected by ``Depends(require_admin)`` — only users
whose JWT carries ``role=admin`` can reach them.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_admin
from app.db.repositories.user_repo import UserRepository
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UpdateUserRoleRequest, UserPublic

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],   # blanket guard for every route below
)


@router.get(
    "/users",
    response_model=list[UserPublic],
    summary="List all users (admin only)",
)
async def list_users(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> list[UserPublic]:
    users = await UserRepository(db).list_all(limit=limit, offset=offset)
    return [UserPublic.model_validate(u) for u in users]


@router.patch(
    "/users/{user_id}/role",
    response_model=UserPublic,
    summary="Change a user's role (admin only — including granting admin)",
)
async def update_user_role(
    user_id: str,
    payload: UpdateUserRoleRequest,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),  # caller is guaranteed admin here
) -> UserPublic:
    repo = UserRepository(db)
    target = await repo.get_by_id(user_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    updated = await repo.update_role(target, payload.role)
    return UserPublic.model_validate(updated)
