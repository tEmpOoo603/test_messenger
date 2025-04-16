import json
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.dependencies import create_ws_service, get_uuid_ws
from app.services.ws_service import WsService
from app.websocket.ws_handler.handler import registry

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
"""
@ws_router.websocket("/connect")
async def connect(
        websocket: WebSocket,
        current_user_uuid: UUID = Depends(get_uuid_ws),
        ws_service: WsService = Depends(create_ws_service),
):
    await websocket.accept()
    while True:
        try:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            action = payload['action']

            handler = registry.get(action)
            if handler is None:
                await websocket.send_json({"detail": f"Unknown action: {action}"})
                continue
            await handler(current_user_uuid, payload, websocket, ws_service)

        except WebSocketDisconnect:
            await ws_service.make_rollback()
            await websocket.send_text(f"{current_user_uuid} disconnected")

        except Exception as e:
            await ws_service.make_rollback()
            await websocket.send_json({"detail": str(e)})
