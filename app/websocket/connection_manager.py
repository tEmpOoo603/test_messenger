from typing import Dict
from uuid import UUID

from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}

    def connect(self, user_uuid: UUID, websocket: WebSocket):
        self.active_connections[user_uuid] = websocket

    def disconnect(self, user_uuid: UUID):
        self.active_connections.pop(user_uuid, None)

    def get(self, user_uuid: UUID) -> WebSocket | None:
        return self.active_connections.get(user_uuid)

    def is_user_online(self, user_uuid: UUID) -> bool:
        return user_uuid in self.active_connections


connection_manager = ConnectionManager()
