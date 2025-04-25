from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Enum as SQLEnam, ForeignKey, Integer, Text, func, UUID
from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()


class ChatType(Enum):
    PRIVATE = "private"
    GROUP = "group"


class ReadStatus(Enum):
    READ = "read"
    UNREAD = "unread"


class User(Base):
    __tablename__ = "users"
    user_uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4())
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]


class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ChatType] = mapped_column(SQLEnam(ChatType, name="chattype"), nullable=False)
    name: Mapped[str]
    creator_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.user_uuid", ondelete="CASCADE"))


class UserChat(Base):
    __tablename__ = "user_chats"
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.user_uuid", ondelete="CASCADE"), primary_key=True, index=True)
    chat: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat: Mapped[int] = mapped_column(ForeignKey("chats.id"), index=True)
    sender_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.user_uuid"))
    text: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    read_status: Mapped[ReadStatus] = mapped_column(SQLEnam(ReadStatus, name="read_status"), nullable=False,
                                                    default=ReadStatus.UNREAD)


class MessageUserRead(Base):
    __tablename__ = "message_user_read"
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.user_uuid"), primary_key=True)
    message: Mapped[int] = mapped_column(ForeignKey("messages.id"), primary_key=True, index=True)
    status: Mapped[ReadStatus] = mapped_column(SQLEnam(ReadStatus, name="read_status"), nullable=False,
                                               default=ReadStatus.UNREAD)
