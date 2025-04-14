from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


def create_user_service(db: AsyncSession = Depends(get_db_session)):
    user_repo = UserRepository(db=db)
    return UserService(user_repo=user_repo)