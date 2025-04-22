from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chats import CreateChat
from app.chats.schemas import ChatOut, MessageOut
from app.database import UserChat, Chat, Message


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, chat_data: CreateChat) -> ChatOut:
        new_chat = Chat(**chat_data.dict(exclude={"user_ids"}))
        self.db.add(new_chat)
        await self.db.flush()
        self.db.add_all([
                            UserChat(user=user_uuid, chat=new_chat.id) for user_uuid in chat_data.user_uuids
                        ] + [UserChat(user=chat_data.creator_uuid, chat=new_chat.id)])
        await self.db.commit()
        return ChatOut.from_orm(new_chat).copy(update={"user_uuids": chat_data.user_uuids})

    async def is_user_in_chat(self, user_uuid: UUID, chat_id: int) -> bool:
        result = await self.db.execute(select(UserChat).where(UserChat.user_uuid == user_uuid, UserChat.chat == chat_id))
        return bool(result.scalars().first())

    async def get_chat_users(self, chat_id: int) -> list[UUID]:
        result = await self.db.execute(select(UserChat.user_uuid).where(UserChat.chat == chat_id))
        return list(result.scalars().all())

    async def get_chat_by_id(self, chat_id: int) -> Chat | None:
        try:
            chat = await self.db.execute(select(Chat).where(Chat.id == chat_id))
            return chat.scalars().first()
        except:
            raise ValueError("detail: Chat not found.")

    async def get_chat_history(self, chat_id: int) -> list[MessageOut]:
        try:
            messages = await self.db.execute(select(Message).where(Message.chat == chat_id).order_by(Message.timestamp.desc()))
            message = messages.scalars().all()
            if not message:
                raise ValueError("detail: No chat history.")
            return [MessageOut.from_orm(m) for m in message]
        except:
            raise ValueError("detail: Messages not found.")