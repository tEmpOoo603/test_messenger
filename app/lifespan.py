from contextlib import asynccontextmanager

from sqlalchemy import text

from app.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        engine.echo = False
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        yield