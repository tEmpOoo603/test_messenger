
from typing import List

from fastapi import FastAPI
from starlette.websockets import WebSocket

from .chats import chat_router
from .controllers.user_controller import users_router

app = FastAPI()
app.include_router(users_router)
app.include_router(chat_router)
active_connections: List[WebSocket] = []

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/create_group")
async def CreateChatView():
    pass






