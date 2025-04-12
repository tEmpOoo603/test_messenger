from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ..chats import CreateChatRequest
from ..database import Chat, UserChat


async def create_chat(db: AsyncSession, chat_data: CreateChatRequest):
    try:
        async with db.begin():
            new_chat = Chat(**chat_data.dict(exclude={"user_ids"}))
            db.add(new_chat)
            await db.flush()
            if chat_data.creator in chat_data.user_ids:
                raise ValueError("Creator cannot be a member of the chat.")
            db.add_all([
                UserChat(user=user_id, chat=new_chat.id) for user_id in chat_data.user_ids
            ] + [UserChat(user=chat_data.creator, chat=new_chat.id)])
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    return new_chat