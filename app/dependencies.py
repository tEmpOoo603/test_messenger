from typing import Optional
from uuid import UUID

from starlette.requests import Request
from starlette.websockets import WebSocket

from app.repositories import ChatRepository, WsRepository, UserRepository
from app.services import ChatService, WsService, UserService
from app.users import get_user_uuid_from_token
from app.database import DBSession

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
