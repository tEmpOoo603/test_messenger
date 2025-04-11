from datetime import datetime
from enum import Enum
from sqlalchemy import Enum as SQLEnam, ForeignKey, Integer, Text, func, UUID
from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()
class ReadStatus(Enum):
    READ = "read"
    UNREAD = "unread"

class User(Base):
    __tablename__ = "users"
    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=func.uuid_generate_v4())
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    chats: Mapped[list["UserChat"]] = relationship("UserChat", back_populates="user_obj")


class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    creator: Mapped[UUID] = mapped_column(ForeignKey("users.uuid", ondelete="CASCADE"))

    members: Mapped[list["UserChat"]] = relationship("UserChat", back_populates="chat_obj")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="chat_obj", cascade="all, delete")


class UserChat(Base):
    __tablename__ = "user_chats"
    user: Mapped[UUID] = mapped_column(ForeignKey("users.uuid", ondelete="CASCADE"), primary_key=True)
    chat: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True)

    user_obj: Mapped["User"] = relationship("User", back_populates="chats")
    chat_obj: Mapped["Chat"] = relationship("Chat", back_populates="members")


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    sender: Mapped[UUID] = mapped_column(ForeignKey("users.uuid"))
    text: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    read_status: Mapped[ReadStatus] = mapped_column(SQLEnam(ReadStatus, name="read_status"), default=ReadStatus.UNREAD)

    chat_obj: Mapped["Chat"] = relationship("Chat", back_populates="messages")