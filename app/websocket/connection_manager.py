from uuid import UUID

from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    def connect(self, user: UUID, websocket: WebSocket):
        self.active_connections[user] = websocket

    def disconnect(self, user: UUID):
        self.active_connections.pop(user, None)

    def get(self, user: UUID) -> WebSocket | None:
        return self.active_connections.get(user)

    def is_user_online(self, user: UUID) -> bool:
        return user in self.active_connections

connection_manager = ConnectionManager()