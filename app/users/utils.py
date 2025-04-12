from typing import Union, Optional
from uuid import UUID
from fastapi import Request
import bcrypt
import jwt
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.websockets import WebSocket

from ..config import settings
from ..database import get_db_session, User
from ..users.schemas import PublicUser


# hash password to store in database
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# check that given password is equal to hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# create JWT token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_uuid_request(request: Request) -> Optional[str]:
    token = request.headers.get("Authorization")
    return await get_user_from_token(token=token)


async def get_uuid_ws(ws: WebSocket) -> Optional[str]:
    token = ws.headers.get("Authorization")
    return await get_user_from_token(token=token)


async def get_user_from_token(token: str = None) -> str:
    try:
        if not token:
            raise HTTPException(status_code=401, detail="Authorization token missing")

        token = token.split(" ")
        if len(token) != 2 or token[0] != "Bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Bearer token")
        token = token[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_uuid = payload.get("sub")
        if user_uuid is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user_uuid
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_users_list(current_user_uuid: UUID, db: AsyncSession = Depends(get_db_session)) -> dict:
    result = await db.execute(select(User).filter(User.uuid != current_user_uuid).order_by(User.name))
    users = result.scalars().all()
    return {'users': [PublicUser.from_orm(user) for user in users]}
