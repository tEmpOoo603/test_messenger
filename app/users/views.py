from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from .schemas import UserCreate, UserOut, Token, LoginData
from .utils import hash_password, verify_password, create_access_token, get_users_list, get_user_from_token, \
    get_uuid_request
from ..database import get_db_session, User

users_router = APIRouter()


@users_router.post("/register", response_model=UserOut)
async def UserRegisterView(user_data: UserCreate, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pwd = hash_password(user_data.password)
    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_pwd
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@users_router.post("/login", response_model=Token)
async def UserLoginView(data: LoginData, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.uuid)})
    return Token(access_token=f"Bearer {access_token}", uuid=user.uuid)


@users_router.get("/users_list")
async def GetUsersView(
                       db: AsyncSession = Depends(get_db_session),
                       current_user_uuid: UUID = Depends(get_uuid_request)):
    return await get_users_list(current_user_uuid=current_user_uuid, db=db)
