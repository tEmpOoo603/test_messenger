from uuid import UUID

from ..repositories import UserRepository
from ..database import User
from ..exceptions import UserException
from ..users import (PublicUser,
                     UserOut,
                     UserCreate,
                     LoginData,
                     Token,
                     hash_password,
                     verify_password,
                     create_access_token)


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def make_rollback(self):
        await self.user_repo.make_rollback()

    async def user_exists(self, email: str) -> bool:
        result = await self.user_repo.get_user_by_email(email=email)
        return bool(result)

    async def get_other_users_list(self, user_uuid: UUID) -> dict[str, list[PublicUser]]:
        return {'users': [PublicUser.model_validate(user) for user in
                          await self.user_repo.get_user_list_without_current(user_uuid=user_uuid)]}

    async def register_user(self, user_data: UserCreate) -> UserOut:
        hashed_pwd = hash_password(user_data.password)
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_pwd
        )
        saved_user = await self.user_repo.add_new_user(user=user)
        user_out = UserOut.model_validate(saved_user)
        return user_out

    async def login_user(self, data: LoginData) -> Token:
        user = await self.user_repo.get_user_by_email(data.email)
        if not user:
            raise UserException("No user matches email")
        if not verify_password(data.password, user.password):
            raise UserException("Invalid credentials")
        access_token = create_access_token(data={"sub": str(user.user_uuid)})
        return Token(access_token=f"Bearer {access_token}", user_uuid=user.user_uuid)
