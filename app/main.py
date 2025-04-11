
from typing import List

import jwt
from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from .auth.views.auth_views import auth_router
from .config import settings

app = FastAPI()
app.include_router(auth_router)

active_connections: List[WebSocket] = []

# async def get_current_user_ws(token: str):
#     try:
#         playload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#
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

