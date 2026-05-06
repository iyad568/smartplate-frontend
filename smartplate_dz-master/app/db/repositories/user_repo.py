from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        return await self.get_by_email(email) is not None

    async def create(
        self,
        *,
        full_name: str,
        email: str,
        phone: str,
        hashed_password: str,
        role: UserRole = UserRole.USER,
    ) -> User:
        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            hashed_password=hashed_password,
            role=role,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def mark_verified(self, user: User) -> User:
        user.is_verified = True
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_role(self, user: User, role: UserRole) -> User:
        user.role = role
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_password(self, user: User, hashed_password: str) -> User:
        user.hashed_password = hashed_password
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: str, update_data: dict) -> User | None:
        """Update user fields."""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        # Update allowed fields
        allowed_fields = ['full_name', 'phone', 'profile_picture']
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(user, field, value)
        
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def list_all(self, *, limit: int = 100, offset: int = 0) -> list[User]:
        result = await self.db.execute(
            select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    
    
