from uuid import UUID

from fastapi import Depends, APIRouter

from app.chats.pagination import chat_paginator
from app.dependencies import get_uuid_request, create_chat_service
from app.exceptions import logger, ChatException

chat_router = APIRouter()


@chat_router.get("/history/{chat_id}")
async def get_chat_history(
        chat_id: int,
        user_uuid: UUID = Depends(get_uuid_request),
        chat_service=Depends(create_chat_service),
        paginator=Depends(chat_paginator)):
    try:
        return await chat_service.get_chat_history(chat_id=chat_id, user_uuid=user_uuid, paginator=paginator)

    except ChatException as e:
        return {"detail": str(e)}

    except Exception as e:
        logger.error(f"Exception in {get_chat_history.__name__}: {e}")