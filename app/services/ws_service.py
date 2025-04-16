from uuid import UUID

from app.chats import CreateChat
from app.chats.schemas import ChatOut
from app.repositories.ws_repository import WsRepository


class WsService:
    def __init__(self, ws_repo: WsRepository):
        self.ws_repo = ws_repo

    async def create_chat(
            self,
            chat_data: CreateChat,
            current_user_uuid: UUID
    ) -> ChatOut:
        chat_data = chat_data.copy(update={"creator": current_user_uuid})
        if chat_data.creator in chat_data.user_ids:
            raise ValueError("Creator cannot be a member of the chat.")
        return await self.ws_repo.create_chat(chat_data=chat_data)

    async def make_rollback(self):
        await self.ws_repo.make_rollback()