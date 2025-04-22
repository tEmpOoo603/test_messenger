from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..exceptions import UserException
from ..exceptions import logger
from ..users.schemas import PublicUser
from app.database import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def make_rollback(self):
        await self.db.rollback()

    async def get_user_by_email(self, email: str) -> User | None:
        try:
            result = await self.db.execute(select(User).where(User.email == email))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Exception in {self.get_user_by_email.__name__}: {e}")
            raise UserException("Can't match mail with user")

    async def get_user_list_without_current(self, user_uuid: UUID) -> list[PublicUser]:
        try:
            result = await self.db.execute(select(User).filter(User.user_uuid != user_uuid).order_by(User.name))
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Exception in {self.get_user_by_email.__name__}: {e}")
            raise UserException("Can't get users list")

    async def add_new_user(self, user: User):
        try:
            self.db.add(user)
            await self.db.commit()
            return user
        except Exception as e:
            await self.make_rollback()
            logger.error(f"Exception in {self.add_new_user.__name__}: {e}")
            raise UserException("Can't create new user.")
