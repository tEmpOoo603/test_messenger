from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chats import CreateChat
from app.chats.schemas import ChatOut, MessageOut
from app.database import UserChat, Chat, Message
from app.exceptions import ChatException
from ..chats.pagination import chat_paginator
from ..exceptions import logger


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def make_rollback(self):
        await self.db.rollback()

    async def create_chat(self, chat_data: CreateChat) -> ChatOut:
        try:
            new_chat = Chat(**chat_data.model_dump(exclude={"user_uuids"}))
            self.db.add(new_chat)
            await self.db.flush()
            self.db.add_all([
                                UserChat(user_uuid=user_uuid, chat_id=new_chat.id) for user_uuid in chat_data.user_uuids
                            ] + [UserChat(user_uuid=chat_data.creator_uuid, chat_id=new_chat.id)])
            await self.db.commit()
            return ChatOut.model_validate(new_chat).model_copy(update={"user_uuids": chat_data.user_uuids})
        except Exception as e:
            await self.make_rollback()
            logger.error(f"Exception in {self.create_chat.__name__}: {e}")
            raise ChatException(f"Failed to create chat")

    async def is_user_in_chat(self, user_uuid: UUID, chat_id: int) -> bool:
        try:
            result = await self.db.execute(
                select(UserChat).where(UserChat.user_uuid == user_uuid, UserChat.chat_id == chat_id))
            return bool(result.scalars().first())
        except Exception as e:
            logger.error(f"Exception in {self.is_user_in_chat.__name__}: {e}")
            raise ChatException(f"Error checking user for chat participant")

    async def get_chat_users(self, chat_id: int) -> list[UUID]:
        try:
            result = await self.db.execute(select(UserChat.user_uuid).where(UserChat.chat_id == chat_id))
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Exception in {self.get_chat_users.__name__}: {e}")
            raise ChatException(f"Error getting chat users")

    async def get_chat_by_id(self, chat_id: int) -> Chat | None:
        try:
            chat = await self.db.execute(select(Chat).where(Chat.id == chat_id))
            return chat.scalars().first()
        except Exception as e:
            logger.error(f"Exception in {self.get_chat_by_id.__name__}: {str(e)}")
            raise ChatException(f"Error getting chat info")

    async def get_chat_history(self, chat_id: int, paginator: dict) -> list[MessageOut]:
        messages = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .offset(paginator["offset"])
            .limit(paginator["limit"])
            .order_by(Message.timestamp.desc()))
        message = messages.scalars().all()
        if not message:
            raise ChatException("detail: No chat history.")
        return [MessageOut.model_validate(m) for m in message]
