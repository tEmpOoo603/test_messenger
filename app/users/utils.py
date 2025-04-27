from uuid import UUID

import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from ..config import settings
from ..exceptions import UserException, logger


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    except Exception as e:
        logger.error(f"Exception in {create_access_token.__name__}: {e}")
        raise


async def get_user_uuid_from_token(token: str = None) -> UUID:
    try:
        if not token:
            raise UserException("Authorization token missing")

        token = token.split(" ")
        if len(token) != 2 or token[0] != "Bearer":
            raise UserException("Invalid Bearer token")
        token = token[1]
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_uuid = payload.get("sub")
        if user_uuid is None:
            raise UserException("Invalid token")
        return UUID(user_uuid)
    except Exception as e:
        logger.error(f"Exception in {get_user_uuid_from_token.__name__}: {e}")
        raise UserException("Invalid token")
