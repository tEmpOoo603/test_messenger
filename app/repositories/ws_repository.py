from typing import Sequence
from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing import db

from app.chats import CreateChat
from app.chats.schemas import ChatOut, CreateMessage, MessageOut
from app.database import Chat, UserChat, Message
from app.database.models import MessageUserRead, ReadStatus


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

    async def is_user_in_chat(self, user_id: str, chat_id: int) -> bool:
        result = await self.db.execute(select(UserChat).where(UserChat.user == user_id, UserChat.chat == chat_id))
        return bool(result.scalars().first())

    async def create_message(self, message: Message, users: list[UUID]) -> MessageOut:
        self.db.add(message)
        await self.db.flush()
        self.db.add_all(
            [MessageUserRead(user=user, message=message.id) for user in users if user != UUID(message.sender)])
        await self.db.commit()
        return MessageOut.from_orm(message)

    async def get_chat_users(self, chat_id: int) -> list[UUID]:
        result = await self.db.execute(select(UserChat.user).where(UserChat.chat == chat_id))
        return list(result.scalars().all())

    async def make_rollback(self):
        await self.db.rollback()

    async def mark_read(self, message_ids: list[int], user_id: UUID) -> Sequence[MessageUserRead]:

        try:
            result = await self.db.execute(
                update(MessageUserRead)
                .where(
                    MessageUserRead.message.in_(message_ids),
                    MessageUserRead.user == user_id
                )
                .values(status=ReadStatus.READ)
                .returning(MessageUserRead)
            )
            await self.db.commit()

            return result.scalars().all()

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise RuntimeError(f"Database error: {e}")

    async def check_messages_read(self, message_ids: list[int]) -> list[int]:
        try:
            stmt = (
                select(MessageUserRead.message)
                .where(MessageUserRead.message.in_(message_ids))
                .group_by(MessageUserRead.message)
                .having(func.bool_and(MessageUserRead.status == ReadStatus.READ))
            )
            result = await self.db.execute(stmt)

            return [row[0] for row in result.fetchall()]
        except Exception:
            raise ValueError("detail: Can't check messages read status.")

    async def get_messages_by_ids(self, messages_ids: list[int]) -> list[Message]:
        try:
            messages = await self.db.execute(select(Message).where(Message.id.in_(messages_ids)))
            message = messages.scalars().all()
            if message is None:
                raise ValueError("detail: Message not found.")
            return list(message)
        except:
            raise ValueError("detail: Message not found.")

    async def get_unread_messages(self, user_id: UUID) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .join(MessageUserRead)
            .where(
                MessageUserRead.user == user_id,
                MessageUserRead.status == ReadStatus.UNREAD
            )
        )
        return list(result.scalars().all())

    async def mark_mes_read(self, messages_ids: list[int]):
        try:
            await self.db.execute(
                update(Message)
                .where(Message.id.in_(messages_ids))
                .values(read_status=ReadStatus.READ)
            )
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            raise RuntimeError(f"Failed to update message read status: {e}")