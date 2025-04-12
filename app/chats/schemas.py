from uuid import UUID

from pydantic import BaseModel, model_validator

from ..database import ChatType


class CreateChatRequest(BaseModel):
    creator: str | None = None
    type: ChatType
    name: str
    user_ids: list[str]

    @model_validator(mode='after')
    def check_private_chat_user_count(self) -> "CreateChatRequest":
        if self.type == ChatType.PRIVATE and len(self.user_ids) != 1:
            raise ValueError("Private chat must have exactly one user_id.")
        if self.creator in self.user_ids:
            raise ValueError("Creator cannot be a member of the chat.")
        return self