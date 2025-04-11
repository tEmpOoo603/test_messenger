from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI
from sqlalchemy import text
from starlette.websockets import WebSocket, WebSocketDisconnect

from .auth.views.auth_views import auth_router
from .config import settings
from .database import engine

app = FastAPI()
app.include_router(auth_router)

active_connections: List[WebSocket] = []
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        engine.echo = False
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        yield

@app.get("/")
async def root():
    return {"message": "Hello World"}
@app.websocket("/ws")
async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Ожидаем сообщения от пользователя
            data = await websocket.receive_text()

            # Отправляем полученное сообщение всем активным пользователям
            for connection in active_connections:
                if connection != websocket:
                    await connection.send_text(f"Message: {data}")
    except WebSocketDisconnect:
        # Удаляем соединение из списка при отключении
        active_connections.remove(websocket)

