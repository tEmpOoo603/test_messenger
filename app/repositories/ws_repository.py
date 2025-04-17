from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.chats import CreateChat
from app.chats.schemas import ChatOut, CreateMessage, MessageOut
from app.database import Chat, UserChat, Message


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
        return ChatOut.from_orm(new_chat).copy(update={"user_ids": chat_data.user_ids})

    async def get_chat_by_id(self, chat_id: int) -> Chat | None:
        try:
            chat = await self.db.execute(select(Chat).where(Chat.id == chat_id))
            return chat.scalars().first()
        except:
            raise ValueError("detail: Chat not found.")

    async def is_user_in_chat(self, user_id: UUID, chat_id: int) -> bool:
        result = await self.db.execute(select(UserChat).where(UserChat.user == user_id, UserChat.chat == chat_id))
        return bool(result.scalars().first())

    async def create_message(self, message: Message) -> MessageOut:
        self.db.add(message)
        await self.db.flush()
        await self.db.commit()
        return MessageOut.from_orm(message)

    async def make_rollback(self):
        await self.db.rollback()
