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

    async def create_message(self, message: Message, users_uuids: list[UUID]) -> MessageOut:
        try:
            self.db.add(message)
            await self.db.flush()
            self.db.add_all(
                [MessageUserRead(user_uuid=user_uuid, message=message.id) for user_uuid in users_uuids if user_uuid != message.sender_uuid])
            await self.db.commit()
            return MessageOut.from_orm(message)
        except:
            await self.make_rollback()
            raise ValueError("Can't create message.")

    async def make_rollback(self):
        await self.db.rollback()

    async def mark_read(self, message_ids: list[int], user_uuid: UUID) -> Sequence[MessageUserRead]:

        try:
            result = await self.db.execute(
                update(MessageUserRead)
                .where(
                    MessageUserRead.message.in_(message_ids),
                    MessageUserRead.user_uuid == user_uuid
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
            if not message:
                raise ValueError("detail: Message not found.")
            return list(message)
        except:
            raise ValueError("detail: Message not found.")

    async def get_unread_messages(self, user_uuid: UUID) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .join(MessageUserRead)
            .where(
                MessageUserRead.user_uuid == user_uuid,
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
            await self.make_rollback()
            raise RuntimeError(f"Failed to update message read status: {e}")
