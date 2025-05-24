from typing import List, Optional, Any, Coroutine, Sequence

from sqlalchemy import select, or_, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.enum.user_role import UserRole
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash


class UserService:
    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        user = User(
            first_name=user_data.first_name,
            email=user_data.email,
            last_name=user_data.last_name,
            role=UserRole.user,
            is_active=True,
            password=hashed_password
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get_users(self, db: AsyncSession) -> Sequence[User]:
        """Get all users"""
        result = await db.execute(
            select(User).options(joinedload(User.resources))
        )
        return result.scalars().all()

    async def get_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get a specific user by ID"""
        result = await db.execute(
            select(User)
            .options(joinedload(User.resources))
            .where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get a user by username"""
        result = await db.execute(
            select(User)
            .options(joinedload(User.resources))
            .where(User.email == email)
        )
        return result.scalars().first()

    async def search_users(
            self,
            db: AsyncSession,
            query: str,
            role: Optional[UserRole] = None,
            is_active: Optional[bool] = None
    ) -> Sequence[User]:
        """Search users by query string"""
        search_query = select(User).options(joinedload(User.resources))

        # Add text search
        if query:
            search_query = search_query.where(
                or_(
                    User.email.ilike(f"%{query}%"),
                )
            )

        # Add role filter
        if role:
            search_query = search_query.where(User.role == role)

        # Add active status filter
        if is_active is not None:
            search_query = search_query.where(User.is_active == is_active)

        result = await db.execute(search_query)
        return result.scalars().all()

    async def update_user_role(
            self, db: AsyncSession, user_id: int, role: UserRole
    ) -> Optional[User]:
        """Update a user's role"""
        user = await self.get_user(db, user_id)
        if user:
            user.role = role
            await db.commit()
            await db.refresh(user)
        return user

    async def deactivate_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Deactivate a user"""
        user = await self.get_user(db, user_id)
        if user:
            user.is_active = False
            await db.commit()
            await db.refresh(user)
        return user

    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        """Delete a user"""
        user = await self.get_user(db, user_id)
        if user:
            await db.delete(user)
            await db.commit()
            return True
        return False
