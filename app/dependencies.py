from typing import Optional
from uuid import UUID

from starlette.requests import Request
from starlette.websockets import WebSocket

from app.repositories.chat_repository import ChatRepository
from app.repositories.user_repository import UserRepository
from app.repositories.ws_repository import WsRepository
from app.services.chat_service import ChatService
from app.services.user_service import UserService
from app.services.ws_service import WsService
from app.users.utils import get_user_uuid_from_token
from app.database.database import DBSession

async def create_user_service(DBSession: DBSession) -> UserService:
    user_repo = UserRepository(db=DBSession)
    return UserService(user_repo=user_repo)


async def create_chat_service(DBSession: DBSession) -> ChatService:
    chat_repo = ChatRepository(db=DBSession)
    return ChatService(chat_repo=chat_repo)

async def create_ws_service(DBSession: DBSession) -> WsService:
    ws_repo = WsRepository(db=DBSession)
    return WsService(ws_repo=ws_repo)


async def get_uuid_request(request: Request) -> UUID:
    token = request.headers.get("Authorization")
    return await get_user_uuid_from_token(token=token)


async def get_uuid_ws(ws: WebSocket) -> UUID:
    token = ws.headers.get("Authorization")
    return await get_user_uuid_from_token(token=token)
