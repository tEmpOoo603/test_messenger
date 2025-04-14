from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.chats import CreateChatRequest
from app.database import UserChat, Chat


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, chat_data: CreateChatRequest):
        try:
            async with self.db.begin():
                new_chat = Chat(**chat_data.dict(exclude={"user_ids"}))
                self.db.add(new_chat)
                await self.db.flush()
                if chat_data.creator in chat_data.user_ids:
                    raise ValueError("Creator cannot be a member of the chat.")
                self.db.add_all([
                               UserChat(user=user_id, chat=new_chat.id) for user_id in chat_data.user_ids
                           ] + [UserChat(user=chat_data.creator, chat=new_chat.id)])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
        return new_chat