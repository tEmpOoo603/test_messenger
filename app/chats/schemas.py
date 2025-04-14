from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel, model_validator

from ..database import ChatType


class CreateChat(BaseModel):
    creator: str | None = None
    type: ChatType
    name: str
    user_ids: list[str]

    @model_validator(mode='after')
    def check_private_chat_user_count(self):
        if self.type == ChatType.PRIVATE and len(self.user_ids) != 1:
            raise HTTPException(status_code=400, detail="Private chat must have exactly one user_id.")
        return self

class ChatOut(BaseModel):
    id: int
    name: str
    type: ChatType
    creator: str
    user_ids: list[str] = None

    class Config:
        from_attributes = True
