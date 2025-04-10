from datetime import datetime
from enum import Enum
from sqlalchemy import Enum as SQLEnam, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP

from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]


class ChatType(Enum):
    PRIVATE = "private"
    GROUP = "group"


class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[ChatType] = mapped_column(SQLEnam(ChatType, name="chat_type"), nullable=False)


"""
Я бы сделал через m2m но по заданию структура базы данных должна быть именно такой
"""
class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    participants: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)

class ReadStatus(Enum):
    READ = "read"
    UNREAD = "unread"

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    read_status: Mapped[ReadStatus] = mapped_column(SQLEnam(ReadStatus, name="read_status"), default=ReadStatus.UNREAD)
