
from typing import List

from fastapi import FastAPI
from starlette.websockets import WebSocket
from .controllers.user_controller import users_router
from .controllers.ws_controller import ws_router
from .lifespan import lifespan

app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(ws_router)
active_connections: List[WebSocket] = []

@app.get("/")
async def root():
    return {"message": "Hello World"}






