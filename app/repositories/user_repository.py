from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..users.schemas import PublicUser
from app.database import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_list_without_current(self, current_user_uuid: UUID) -> list[PublicUser]:
        result = await self.db.execute(select(User).filter(User.uuid != current_user_uuid).order_by(User.name))
        return list(result.scalars().all())

    async def add_new_user(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
