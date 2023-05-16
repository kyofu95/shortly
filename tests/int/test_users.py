import pytest
from httpx import AsyncClient

from shortly.schemas.user import UserInDB
from shortly.api.v1.Depends.oauth import get_current_user
from shortly.main import app


@pytest.mark.asyncio
async def test_create(setup_client: AsyncClient):
    client = setup_client

    new_user = {"login": "new_test_user", "password": "super_secure_password"}

    response = await client.post("api/users", json=new_user)
    assert response.status_code == 201

    response = await client.post("api/users", json=new_user)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_user_me(setup_client: AsyncClient):
    client = setup_client

    async def skip_auth():
        return {"login": "user1", "id": 1, "create_at": "2023-01-01T02:10:12.777785", "disabled": "False", "links": []}

    app.dependency_overrides[get_current_user] = skip_auth

    response = await client.get("api/users/me")
    assert response.status_code == 200

    app.dependency_overrides = {}

    response = await client.get("api/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_delete(setup_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    client = setup_client

    response = await client.delete("api/users/5")
    assert response.status_code == 401

    async def skip_auth():
        user_dict = {
            "login": "user1",
            "id": 5,
            "create_at": "2023-01-01T02:10:12.777785",
            "disabled": "False",
            "refresh_token": "",
            "links": [],
        }
        return UserInDB(**user_dict)

    app.dependency_overrides[get_current_user] = skip_auth

    async def repo_disable(*_):
        pass

    monkeypatch.setattr("shortly.api.v1.users.UserRepository.disable", repo_disable)

    response = await client.delete("api/users/5")
    assert response.status_code == 204

    app.dependency_overrides = {}
