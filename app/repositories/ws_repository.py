from typing import Sequence
from uuid import UUID

from sqlalchemy import select, update, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from ..chats import MessageOut
from ..database import Message, MessageUserRead, ReadStatus
from ..exceptions import WSException, logger


class WsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def make_rollback(self):
        await self.db.rollback()

    async def create_message(self, message: Message, users_uuids: list[UUID]) -> MessageOut:
        try:
            self.db.add(message)
            await self.db.flush()
            self.db.add_all(
                [MessageUserRead(user_uuid=user_uuid, message=message.id) for user_uuid in users_uuids if
                 user_uuid != message.sender_uuid])
            await self.db.commit()
            return MessageOut.model_validate(message)
        except Exception as e:
            await self.make_rollback()
            logger.error(f"Exception in {self.create_message.__name__}: {e}")
            raise WSException("Can't create message.")

    async def mark_read(self, message_ids: list[int], user_uuid: UUID) -> Sequence[MessageUserRead]:
        try:
            result = await self.db.execute(
                update(MessageUserRead)
                .where(
                    MessageUserRead.message.in_(message_ids),
                    MessageUserRead.user_uuid == user_uuid,
                    MessageUserRead.status == ReadStatus.UNREAD
                )
                .values(status=ReadStatus.READ)
                .returning(MessageUserRead)
            )
            await self.db.commit()

            return result.scalars().all()

        except Exception as e:
            await self.make_rollback()
            logger.error(f"Exception in {self.mark_read.__name__}: {e}")
            raise WSException("Can't mark message as read.")

    async def check_messages_read(self, message_ids: list[int]) -> list[int]:
        try:
            stmt = (
                select(MessageUserRead.message)
                .where(MessageUserRead.message.in_(message_ids))
                .group_by(MessageUserRead.message)
                .having(func.sum(case((MessageUserRead.status == ReadStatus.UNREAD, 1), else_=0)) == 0)
            )
            result = await self.db.execute(stmt)

            return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Exception in {self.check_messages_read.__name__}: {e}")
            raise WSException("Can't check message read status.")

    async def get_messages_by_ids(self, messages_ids: list[int]) -> list[Message]:
        try:
            messages = await self.db.execute(select(Message).where(Message.id.in_(messages_ids)))
            message = messages.scalars().all()
            if not message:
                raise WSException("Message not found.")
            return list(message)
        except:
            logger.error(f"Exception in {self.get_messages_by_ids.__name__}: {e}")
            raise WSException("Can't get message.")

    async def get_unread_messages(self, user_uuid: UUID) -> list[Message]:
        try:
            result = await self.db.execute(
                select(Message)
                .join(MessageUserRead)
                .where(
                    MessageUserRead.user_uuid == user_uuid,
                    MessageUserRead.status == ReadStatus.UNREAD
                )
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Exception in {self.get_unread_messages.__name__}: {e}")
            raise WSException("Can't get unread messages.")

    async def mark_mes_read(self, messages_ids: list[int]) -> Sequence[Message]:
        try:
            updated = await self.db.execute(
                update(Message)
                .where(
                    Message.id.in_(messages_ids),
                    Message.read_status == ReadStatus.UNREAD)
                .values(read_status=ReadStatus.READ)
                .returning(Message)
            )
            await self.db.commit()
            return updated.scalars().all()
        except Exception as e:
            await self.make_rollback()
            logger.error(f"Exception in {self.mark_mes_read.__name__}: {e}")
            raise WSException("Can't mark messages as read.")
