from datetime import datetime
from typing import Text, Optional
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel, model_validator, ConfigDict

from ..database import ChatType, ReadStatus


class CreateChat(BaseModel):
    creator_uuid: UUID | None = None
    type: ChatType
    name: str
    user_uuids: list[UUID]

    @model_validator(mode='after')
    def check_private_chat_user_count(self):
        if self.type == ChatType.PRIVATE and len(self.user_uuids) != 1:
            raise ValueError("Private chat must have exactly one user.")
        return self


class ChatOut(BaseModel):
    id: int
    name: str
    type: ChatType
    creator_uuid: UUID
    user_uuids: Optional[list[UUID]] = None
    model_config = ConfigDict(from_attributes=True)
    model_config['use_enum_values'] = True


class CreateMessage(BaseModel):
    chat_id: int
    text: str
    sender_uuid: UUID = None


class MessageOut(BaseModel):
    id: int
    chat_id: int
    sender_uuid: UUID
    text: str
    timestamp: datetime
    read_status: ReadStatus
    model_config = ConfigDict(from_attributes=True)
    model_config['use_enum_values'] = True
