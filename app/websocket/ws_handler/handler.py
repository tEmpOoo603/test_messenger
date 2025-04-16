from typing import Callable, Awaitable, Dict
from uuid import UUID

from fastapi import Depends
from starlette.websockets import WebSocket

from app.chats import CreateChat
from app.dependencies import create_ws_service
from app.services.ws_service import WsService

HandlerType = Callable[[UUID, dict, WebSocket], Awaitable[None]]

registry: Dict[str, HandlerType] = {}

def register_action(action: str):
    def wrapper(func: HandlerType):
        registry[action] = func
        return func
    return wrapper

@register_action("create_chat")
async def ws_create_chat(
        current_user_uuid: UUID,
        payload: dict,
        ws: WebSocket,
        ws_service: WsService
):
    chat = CreateChat(**payload)
    chat = await ws_service.create_chat(chat_data=chat, current_user_uuid=current_user_uuid)
    await ws.send_json({"action": "create_chat", "data": chat.model_dump()})

