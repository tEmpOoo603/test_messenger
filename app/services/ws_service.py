from uuid import UUID

from app.chats import CreateChat
from app.chats.schemas import ChatOut, CreateMessage, MessageOut
from app.database import Message
from app.repositories.ws_repository import WsRepository


class WsService:
    def __init__(self, ws_repo: WsRepository):
        self.ws_repo = ws_repo

    async def create_chat(self, chat_data: CreateChat) -> ChatOut:

        if chat_data.creator in chat_data.user_ids:
            raise ValueError("Creator cannot be a member of the chat.")

        return await self.ws_repo.create_chat(chat_data=chat_data)

    async def send_message(self, message: CreateMessage) -> MessageOut:

        if await self.ws_repo.get_chat_by_id(message.chat) is None:
            raise ValueError("Chat not found.")
        elif await self.ws_repo.is_user_in_chat(message.sender, message.chat) is False:
            raise ValueError("User not in chat.")

        message = Message(**message.dict())

        return await self.ws_repo.create_message(message=message)

    async def make_rollback(self):
        await self.ws_repo.make_rollback()
