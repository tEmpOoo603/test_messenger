from fastapi import FastAPI

from .controllers import chat_router, ws_router, users_router
from .exceptions import register_exception_handler
from .lifespan import lifespan

app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(ws_router)
app.include_router(chat_router)
register_exception_handler(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}
