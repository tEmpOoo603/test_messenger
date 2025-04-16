from sqlalchemy.ext.asyncio import AsyncSession

from app.chats import CreateChat
from app.chats.schemas import ChatOut
from app.database import Chat, UserChat


class WsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, chat_data: CreateChat) -> ChatOut:
        new_chat = Chat(**chat_data.dict(exclude={"user_ids"}))
        self.db.add(new_chat)
        await self.db.flush()
        self.db.add_all([
            UserChat(user=user_id, chat=new_chat.id) for user_id in chat_data.user_ids
        ] + [UserChat(user=chat_data.creator, chat=new_chat.id)])
        await self.db.commit()
        return ChatOut.from_orm(new_chat).copy(update={"user_ids":chat_data.user_ids})

    async def make_rollback(self):
        await self.db.rollback()