import logging
from typing import List

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket

from .controllers.chat_controller import chat_router
from .controllers.user_controller import users_router
from .controllers.ws_controller import ws_router
from .exceptions import UserException, ChatException, logger, register_exception_handler
from .lifespan import lifespan

app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(ws_router)
app.include_router(chat_router)
register_exception_handler(app)
@app.get("/")
async def root():
    return {"message": "Hello World"}






