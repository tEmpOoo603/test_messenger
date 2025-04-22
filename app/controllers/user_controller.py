from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import create_user_service, get_uuid_request
from ..services.user_service import UserService
from ..users.schemas import UserOut, UserCreate, LoginData, Token

users_router = APIRouter()


@users_router.post("/register", response_model=UserOut)
async def UserRegisterView(
        user_data: UserCreate,
        user_service: UserService = Depends(create_user_service)
):
    if await user_service.user_exists(email=user_data.email):
        raise HTTPException(status_code=400, detail="User already exists")

    return await user_service.register_user(user_data=user_data)


@users_router.post("/login", response_model=Token)
async def UserLoginView(
        data: LoginData,
        user_service: UserService = Depends(create_user_service)
):
    return await user_service.login_user(data=data)


@users_router.get("/users_list")
async def GetUsersView(
        user_service: UserService = Depends(create_user_service),
        user_uuid: UUID = Depends(get_uuid_request)):
    return await user_service.get_other_users_list(user_uuid=user_uuid)
