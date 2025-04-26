from typing import Callable, Awaitable, Dict
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from starlette.websockets import WebSocket

from ..chats import CreateChat, CreateMessage
from ..services import WsService

HandlerType = Callable[[UUID, dict, WebSocket, WsService], Awaitable[None]]

registry: Dict[str, HandlerType] = {}


def register_action(action: str):
    def wrapper(func: HandlerType):
        registry[action] = func
        return func

    return wrapper


@register_action("create_chat")
async def ws_create_chat(
        user_uuid: UUID,
        payload: dict,
        ws: WebSocket,
        ws_service: WsService
):
    chat_data = CreateChat(**payload).model_copy(update={"creator_uuid": user_uuid})
    new_chat = await ws_service.create_chat(chat_data=chat_data)
    await ws.send_json({"action": "create_chat", "data": new_chat.model_dump(mode="json")})


@register_action("send_message")
async def ws_send_message(
        user_uuid: UUID,
        payload: dict,
        ws: WebSocket,
        ws_service: WsService
):
    message = CreateMessage(**payload).copy(update={"sender_uuid": user_uuid})
    message_data = await ws_service.create_message(message=message)
    await ws.send_json({"action": "message", "data": jsonable_encoder(message_data)})


@register_action("mark_read")
async def ws_mark_read(
        user_uuid: UUID,
        payload: dict,
        ws: WebSocket,
        ws_service: WsService
):
    message_ids: list[int] = payload.get("message_ids")
    readen_message_ids: list[int] = await ws_service.mark_read(message_ids=message_ids, user_uuid=user_uuid)
    await ws.send_json({"action": "readed", "data": {"message_ids": readen_message_ids}})
