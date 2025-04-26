import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from .database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("TESTING") != "1":
        async with engine.begin() as conn:
            engine.echo = True
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            await conn.commit()
    yield
