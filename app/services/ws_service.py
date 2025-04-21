from uuid import UUID

from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocket

from app.chats import CreateChat
from app.chats.schemas import ChatOut, CreateMessage, MessageOut
from app.database import Message
from app.repositories.ws_repository import WsRepository
from app.websocket.connection_manager import connection_manager


class WsService:
    def __init__(self, ws_repo: WsRepository):
        self.ws_repo = ws_repo

    async def create_chat(self, chat_data: CreateChat) -> ChatOut:

        if chat_data.creator_uuid in chat_data.user_uuids:
            raise ValueError("Creator cannot be a member of the chat.")

        return await self.ws_repo.create_chat(chat_data=chat_data)

    async def chat_send_message(self, message: MessageOut, users_uuid: list[UUID]):
        for user_uuid in users_uuid:
            user_websocket = connection_manager.get(user_uuid)
            if user_websocket and user_uuid != message.sender_uuid:
                await user_websocket.send_json({"action": "message", "data": jsonable_encoder(message)})

    async def create_message(self, message: CreateMessage) -> MessageOut:

        if await self.ws_repo.get_chat_by_id(message.chat) is None:
            raise ValueError("Chat not found.")
        elif await self.ws_repo.is_user_in_chat(message.sender_uuid, message.chat) is False:
            raise ValueError("User not in chat.")

        message = Message(**message.dict())

        users_uuids: list[UUID] = await self.ws_repo.get_chat_users(message.chat)
        created_message = await self.ws_repo.create_message(message=message, users_uuids=users_uuids)
        await self.chat_send_message(message=created_message, users_uuid=users_uuids)

        return created_message

    async def make_rollback(self):
        await self.ws_repo.make_rollback()

    async def notify_messages_read(self, messages_ids: list[int]):
        messages = await self.ws_repo.get_messages_by_ids(messages_ids=messages_ids)
        for message in messages:
            user_websocket = connection_manager.get(message.sender_uuid)
            if user_websocket:
                await user_websocket.send_json(
                    {"action": "message_read", "data": {"text": f"Message {message.id} has been read."}})

    async def mark_read(self, message_ids: list[int], user_uuid: UUID) -> None:
        try:
            updated = await self.ws_repo.mark_read(message_ids=message_ids, user_uuid=user_uuid)
            if len(updated) == 0:
                raise ValueError("No message to read or already read.")

            readen_message_ids: list[int] = await self.ws_repo.check_messages_read(message_ids=[message.message for message in updated])
            if readen_message_ids:
                await self.ws_repo.mark_mes_read(messages_ids=readen_message_ids)
                await self.notify_messages_read(messages_ids=readen_message_ids)
        except:
            await self.make_rollback()
            raise ValueError("Can't mark message read.")

    async def unread_messages(self, user_uuid: UUID, websocket: WebSocket) -> None:
        messages = await self.ws_repo.get_unread_messages(user_uuid=user_uuid)
        if messages is not None:
            data = [MessageOut.from_orm(msg).dict() for msg in messages]
            await websocket.send_json({"action": "unread_messages", "data": jsonable_encoder(data)})
