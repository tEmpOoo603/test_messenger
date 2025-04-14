from uuid import UUID

from fastapi import HTTPException

from app.chats import CreateChat
from app.chats.schemas import ChatOut
from app.repositories.chat_repository import ChatRepository


class ChatService:
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo

    async def create_chat(self, chat_data: CreateChat, current_user_uuid: UUID) -> ChatOut:
        chat_data = chat_data.copy(update={"creator": current_user_uuid})
        if chat_data.creator in chat_data.user_ids:
            raise HTTPException(status_code=400, detail="Creator cannot be a member of the chat.")
        return await self.chat_repo.create_chat(chat_data=chat_data)
