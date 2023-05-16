import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture(scope="module")
async def setup_user_for_auth(setup_client: AsyncClient) -> None:
    client = setup_client

    new_user = {"login": "new_test_user_b1", "password": "super_secure_password"}

    response = await client.post("api/users", json=new_user)


@pytest.mark.asyncio
async def test_auth_token(setup_client: AsyncClient, setup_user_for_auth: None):
    client = setup_client

    response = await client.post(
        "api/token",
        data={"username": "new_test_user_b1", "password": "super_secure_password", "grant_type": "password"},
    )
    assert response.status_code == 200

    response = await client.post(
        "api/token",
        data={"username": "unvalid_user", "password": "super_secure_password", "grant_type": "password"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_refresh_token(setup_client: AsyncClient, setup_user_for_auth: None):
    client = setup_client

    response = await client.post(
        "api/token",
        data={"username": "new_test_user_b1", "password": "super_secure_password", "grant_type": "password"},
    )

    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]

    response = await client.post("api/refresh-token", params={"refresh_token": refresh_token})
    assert response.status_code == 200

    response = await client.post("api/refresh-token", params={"refresh_token": access_token})
    assert response.status_code == 400

    response = await client.post("api/refresh-token", params={"refresh_token": ""})
    assert response.status_code == 401

    response = await client.post("api/refresh-token")
    assert response.status_code == 422
