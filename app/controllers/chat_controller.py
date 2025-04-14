from uuid import UUID

from fastapi import APIRouter, Depends

from app.chats import CreateChat
from app.chats.schemas import ChatOut
from app.database import User
from app.dependencies import create_chat_service, get_uuid_request

chat_router = APIRouter()


@chat_router.post("/create-chat", response_model=ChatOut)
async def CreateChatView(
        chat_data: CreateChat,
        current_user_uuid: User = Depends(get_uuid_request),
        chat_service=Depends(create_chat_service)
):
    return await chat_service.create_chat(chat_data=chat_data, current_user_uuid=current_user_uuid)
