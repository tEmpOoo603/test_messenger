from uuid import UUID

from fastapi import Depends, APIRouter

from app.dependencies import get_uuid_request, create_chat_service

chat_router = APIRouter()


@chat_router.get("/history/{chat_id}")
async def get_chat_history(
        chat_id: int,
        user_uuid: UUID = Depends(get_uuid_request),
        chat_service=Depends(create_chat_service)):
    return await chat_service.get_chat_history(chat_id=chat_id, user_uuid=user_uuid)
