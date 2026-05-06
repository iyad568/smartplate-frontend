"""
Routes available to any authenticated user.
"""
from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import UserPublic

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPublic, summary="Get my profile (any role)")
async def me(user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(user)





