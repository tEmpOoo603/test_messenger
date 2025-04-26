import asyncio
import json
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from pydantic import ValidationError
from app.dependencies import create_ws_service, get_uuid_ws
from app.exceptions import WSException, ChatException, UserException
from app.exceptions import logger
from app.services.ws_service import WsService
from app.websocket.connection_manager import connection_manager
from app.websocket.handler import registry

ws_router = APIRouter(tags=["WebSocket"])

@ws_router.websocket("/connect")
async def connect(
    websocket: WebSocket,
    user_uuid: UUID = Depends(get_uuid_ws),
    ws_service: WsService = Depends(create_ws_service),
):
    await websocket.accept()
    connection_manager.connect(user_uuid, websocket)
    logger.warning(f"User {user_uuid} connected")

    try:
        await ws_service.unread_messages(user_uuid, websocket)

        while True:
            try:
                raw = await websocket.receive_text()
                payload = json.loads(raw)

                action = payload.get("action")
                if not action:
                    await websocket.send_json({"detail": "Missing 'action' field"})
                    continue

                handler = registry.get(action)
                if not handler:
                    await websocket.send_json({"detail": f"Unknown action: {action}"})
                    continue

                await handler(user_uuid, payload, websocket, ws_service)

            except json.JSONDecodeError:
                await websocket.send_json({"detail": "Invalid JSON format"})

            except ValidationError as e:
                await websocket.send_json({"detail": str(e)})

            except (WSException, ChatException, UserException) as e:
                await websocket.send_json({"detail": str(e)})

            except Exception as e:
                logger.error(f"Exception inside receive loop in {connect.__name__}: {e}")
                await websocket.send_json({"detail": "Internal server error"})

    except WebSocketDisconnect:
        logger.warning(f"User {user_uuid} disconnected")
        connection_manager.disconnect(user_uuid)

    except Exception as e:
        logger.error(f"Exception outside receive loop in {connect.__name__}: {e}")
        connection_manager.disconnect(user_uuid)