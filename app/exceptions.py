import logging

from fastapi import FastAPI
from starlette.responses import JSONResponse

logger = logging.getLogger("app")


class UserException(Exception):
    pass


class WSException(Exception):
    pass


class ChatException(Exception):
    pass


def register_exception_handler(app: FastAPI):
    @app.exception_handler(UserException)
    async def handle_user_exception(request, exc: UserException):
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @app.exception_handler(WSException)
    async def handle_ws_exception(request, exc: WSException):
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @app.exception_handler(ChatException)
    async def handle_chat_exception(request, exc: ChatException):
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @app.exception_handler(Exception)
    async def handle_exception(request, exc: Exception):
        logger.exception(f"Exception in {request.url.path}: {exc}")
        return JSONResponse({"detail": str(exc)}, status_code=500)
