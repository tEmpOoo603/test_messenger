from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import CreateChatRequest, create_chat
from ..database import get_db_session, User
from ..users.utils import get_uuid_request

chat_router = APIRouter()


@chat_router.post("/create_chat")
async def CreateChatView(
        request_data: CreateChatRequest,
        db: AsyncSession = Depends(get_db_session),
        current_user_uuid: User = Depends(get_uuid_request),
):
    chat_data = request_data.copy(update={"creator": current_user_uuid})
    chat = await create_chat(db=db, chat_data=chat_data)
    return {"chat_id": chat.id}
