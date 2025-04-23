from uuid import UUID

from app.chats import CreateChat
from app.chats.schemas import ChatOut, MessageOut
from app.exceptions import ChatException
from app.repositories.chat_repository import ChatRepository


class ChatService:
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo

    async def get_chat_history(self, chat_id: int, user_uuid: UUID, paginator: dict) -> list[MessageOut]:
        if not await self.chat_repo.is_user_in_chat(user_uuid, chat_id):
            raise ChatException("User not in chat.")
        return await self.chat_repo.get_chat_history(chat_id=chat_id, paginator=paginator)
