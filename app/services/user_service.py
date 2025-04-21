from typing import Optional
from uuid import UUID

from app.repositories.user_repository import UserRepository
from fastapi import Request
import jwt

from fastapi import HTTPException
from ..database import User
from ..users.schemas import PublicUser, UserOut, UserCreate, LoginData, Token
from ..users.utils import hash_password, verify_password, create_access_token


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def user_exists(self, email: str) -> bool:
        result = await self.user_repo.get_user_by_email(email=email)
        return bool(result)

    async def get_other_users_list(self, user_uuid: UUID) -> dict[str, list[PublicUser]]:
        return {'users': [PublicUser.from_orm(user) for user in
                          await self.user_repo.get_user_list_without_current(user_uuid=user_uuid)]}

    async def make_rollback(self):
        await self.user_repo.make_rollback()

    async def register_user_service(self, user_data: UserCreate) -> UserOut:
        try:
            hashed_pwd = hash_password(user_data.password)
            user = User(
                name=user_data.name,
                email=user_data.email,
                password=hashed_pwd
            )
            saved_user = await self.user_repo.add_new_user(user=user)

            user_out = UserOut.from_orm(saved_user)
            return user_out
        except Exception as e:
            await self.make_rollback()
            raise HTTPException(status_code=500, detail=str(e))


    async def login_user_service(self, data: LoginData) -> Token:
        user = await self.user_repo.get_user_by_email(data.email)
        if not user or not verify_password(data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        access_token = create_access_token(data={"sub": str(user.user_uuid)})
        return Token(access_token=f"Bearer {access_token}", user_uuid=user.user_uuid)
