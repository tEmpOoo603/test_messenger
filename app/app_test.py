import os

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from starlette.testclient import TestClient

from .database import Base, get_db_session
from .main import app
import pytest

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://127.0.0.1") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def set_testing_env():
    os.environ["TESTING"] = "1"
    yield


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
    response = await async_client.post("/register",
                                       json={"email": "example@email.com", "password": "testpwd", "name": "testname"})
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


@pytest.mark.asyncio
async def test_user_list(async_client):
    auth_data = {"email": "example@email.com", "password": "testpwd", "name": "testname"}
    auth_data2 = {"email": "example2@email.com", "password": "testpwd", "name": "testname2"}

    reg1 = await async_client.post("/register", json=auth_data)
    assert reg1.status_code == 200

    log1 = await async_client.post("/login", json=auth_data)
    assert log1.status_code == 200
    token1 = log1.json()['access_token']

    response = await async_client.get("/users_list", headers={"Authorization": token1})
    assert response.status_code == 200
    assert not response.json()['users']

    reg2 = await async_client.post("/register", json=auth_data2)
    assert reg2.status_code == 200

    log2 = await async_client.post("/login", json=auth_data2)
    assert log2.status_code == 200
    uuid2 = log2.json()['user_uuid']

    response = await async_client.get("/users_list", headers={"Authorization": token1})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data['users']) == 1
    assert response_data['users'][0]['user_uuid'] == uuid2


def test_ws_create_chat():
    with TestClient(app) as client:
        auth_data = {"email": "example@email.com", "password": "testpwd", "name": "testname"}
        auth_data2 = {"email": "example2@email.com", "password": "testpwd", "name": "testname2"}

        reg1 = client.post("/register", json=auth_data)
        assert reg1.status_code == 200

        log1 = client.post("/login", json=auth_data)
        assert log1.status_code == 200
        token1 = log1.json()['access_token']

        reg2 = client.post("/register", json=auth_data2)
        assert reg2.status_code == 200

        log2 = client.post("/login", json=auth_data2)
        assert log2.status_code == 200
        uuid2 = log2.json()['user_uuid']

        with client.websocket_connect("/connect", headers={"Authorization": token1}) as websocket:
            message = {
                "action": "create_chat",
                "name": "chat1",
                "type": "private",
                "user_uuids": [uuid2]
            }
            websocket.send_json(message)
            response = websocket.receive_json()
            assert response["action"] == "create_chat"
            assert response["data"]['id'] == 1


def test_ws_send_message():
    with TestClient(app) as client1:
        with TestClient(app) as client2:
            auth_data = {"email": "example@email.com", "password": "testpwd", "name": "testname"}
            auth_data2 = {"email": "example2@email.com", "password": "testpwd", "name": "testname2"}

            reg1 = client1.post("/register", json=auth_data)
            assert reg1.status_code == 200

            log1 = client1.post("/login", json=auth_data)
            assert log1.status_code == 200
            token1 = log1.json()['access_token']

            reg2 = client2.post("/register", json=auth_data2)
            assert reg2.status_code == 200

            log2 = client2.post("/login", json=auth_data2)
            assert log2.status_code == 200
            uuid2 = log2.json()['user_uuid']
            token2 = log2.json()['access_token']

            with client1.websocket_connect("/connect", headers={"Authorization": token1}) as websocket1:
                with client2.websocket_connect("/connect", headers={"Authorization": token2}) as websocket2:
                    message = {
                        "action": "create_chat",
                        "name": "chat1",
                        "type": "private",
                        "user_uuids": [uuid2]
                    }
                    websocket1.send_json(message)
                    response = websocket1.receive_json()
                    chat_id = response["data"]['id']
                    mes_text = "hello"
                    message = {
                        "action": "send_message",
                        "chat_id": chat_id,
                        "text": mes_text
                    }
                    websocket1.send_json(message)
                    response = websocket1.receive_json()
                    assert response["action"] == "message"

                    response2 = websocket2.receive_json()
                    assert response2["action"] == "message"
                    assert response2["data"]['text'] == mes_text

                    read_mes_data = {
                        "action": "mark_read",
                        "message_ids": [response["data"]['id']]
                    }

                    websocket2.send_json(read_mes_data)
                    response2 = websocket2.receive_json()
                    assert response2["action"] == "readed"
                    assert response2["data"]['message_ids'] == [response["data"]['id']]

                    response1 = websocket1.receive_json()
                    assert response1["action"] == "message_read"
                    assert response1["data"]['text']

            chat_history_res = client1.get(f"/history/{chat_id}", headers={"Authorization": token1})
            assert chat_history_res.status_code == 200
            chat_history = chat_history_res.json()
            assert chat_history['messages'][0]['text'] == mes_text
