from uuid import UUID

from fastapi import Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from ..main import app, active_connections
from ..dependencies import get_uuid_ws


@app.websocket("/ws")
async def connect(websocket: WebSocket, current_user_uuid: str = Depends(get_uuid_ws)):

    await websocket.accept()
    active_connections.append(websocket)
    for connection in active_connections:
        await connection.send_text(f"Connected: {current_user_uuid}")
    try:
        while True:
            # Ожидаем сообщения от пользователя
            data = await websocket.receive_text()

            # Отправляем полученное сообщение всем активным пользователям
            for connection in active_connections:
                if connection != websocket:
                    await connection.send_text(f"Message: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)