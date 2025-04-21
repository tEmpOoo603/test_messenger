import json
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.dependencies import create_ws_service, get_uuid_ws
from app.services.ws_service import WsService
from app.websocket.connection_manager import connection_manager
from app.websocket.handler import registry

ws_router = APIRouter(
    tags=["WebSocket"],
    responses={404: {"description": "Not found"}},
)

"""
{
    "action":"create_chat",
    "type":"group",
    "name":"ws_ch12at3",
    "user_ids":["9ed2abf3-d191-4967-b034-fee03bf43dba","47202541-1342-4348-84ce-af30fdcfee87"]
}
{
    "action":"message",
    "chat":10,
    "text":"hello chat 5"
}
{
    "action":"message_read",
    "message_id":10
}
"""


@ws_router.websocket("/connect")
async def connect(
    websocket: WebSocket,
    user_uuid: UUID = Depends(get_uuid_ws),
    ws_service: WsService = Depends(create_ws_service),
):
    await websocket.accept()
    connection_manager.connect(user_uuid, websocket)
    try:
        await ws_service.unread_messages(user_uuid, websocket)

        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            action = payload.get("action")

            handler = registry.get(action)
            if not handler:
                await websocket.send_json({"detail": f"Unknown action: {action}"})
                continue

            await handler(user_uuid, payload, websocket, ws_service)

    except WebSocketDisconnect:
        pass  # просто выходим

    finally:
        connection_manager.disconnect(user_uuid)
        try:
            await websocket.close()
        except Exception:
            pass
