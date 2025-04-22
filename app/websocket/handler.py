from typing import Callable, Awaitable, Dict
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette.websockets import WebSocket

from app.chats import CreateChat
from app.chats.schemas import CreateMessage
from app.exceptions import ChatException, UserException, WSException, logger
from app.services.ws_service import WsService

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
    try:
        chat_data = CreateChat(**payload).copy(update={"creator_uuid": user_uuid})
        new_chat = await ws_service.create_chat(chat_data=chat_data)
        await ws.send_json({"action": "create_chat", "data": new_chat.model_dump(mode="json")})

    except ValidationError:
        await ws.send_json({"detail": "Incorrect chat parameters."})
    except Exception as e:
        logger.error(f"Exception in {ws_create_chat.__name__}: {e}")
        await ws.send_json({"detail": "Failed to create chat."})


@register_action("send_message")
async def ws_send_message(
        user_uuid: UUID,
        payload: dict,
        ws: WebSocket,
        ws_service: WsService
):
    try:
        message = CreateMessage(**payload).copy(update={"sender_uuid": user_uuid})
        message_data = await ws_service.create_message(message=message)
        await ws.send_json({"action": "message", "data": jsonable_encoder(message_data)})

    except ValueError as e:
        await ws.send_json({"detail": str(e)})

    except Exception as e:
        await ws.send_json({"detail": "Failed to send message."})


@register_action("mark_read")
async def ws_mark_read(
        user_uuid: UUID,
        payload: dict,
        ws: WebSocket,
        ws_service: WsService
):
    try:
        message_ids: list[int] = payload.get("message_ids")
        await ws_service.mark_read(message_ids=message_ids, user_uuid=user_uuid)
    except (WSException, UserException, ChatException) as e:
        await ws.send_json({"detail": e})
