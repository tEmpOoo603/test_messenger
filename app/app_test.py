import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import Base, get_db_session
from app.main import app
import pytest

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://127.0.0.1") as client:
        yield client

@pytest_asyncio.fixture(autouse=True)
async def override_get_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def _override_get_db() -> AsyncSession:
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db_session] = _override_get_db
    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_registration(async_client):
    response = await async_client.post("/register", json={"email": "example@email.com", "password": "testpwd", "name":"testname"})
    assert response.status_code == 200
    response_data = response.json()
    assert "user_uuid" in response_data

@pytest.mark.asyncio
async def test_login(async_client):
    auth_data = {"email": "example@email.com", "password": "testpwd", "name": "testname"}
    response = await async_client.post("/register", json=auth_data)
    assert response.status_code == 200
    response = await async_client.post("/login", json=auth_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["access_token"]
