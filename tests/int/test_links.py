import pytest
import pytest_asyncio
from httpx import AsyncClient

from shortly.api.v1.Depends.oauth import get_current_user
from shortly.main import app


@pytest_asyncio.fixture(scope="module")
async def setup_user(setup_client: AsyncClient) -> dict[str, str]:
    client = setup_client

    new_user = {"login": "new_test_user_a1", "password": "super_secure_password"}

    response = await client.post("api/users", json=new_user)
    response = await client.post(
        "api/token",
        data={"username": "new_test_user_a1", "password": "super_secure_password", "grant_type": "password"},
    )
    response_data = response.json()

    headers = {"Authorization": "Bearer " + response_data["access_token"]}

    yield headers


@pytest.mark.asyncio
async def test_create_link(setup_client: AsyncClient, setup_user: dict[str, str]):
    client = setup_client
    auth_headers = setup_user

    og_link = {"original_url": "http://example.com"}

    response = await client.post("api/links", json=og_link)
    assert response.status_code == 401

    response = await client.post("api/links", json=og_link, headers=auth_headers)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_links(setup_client: AsyncClient, setup_user: dict[str, str]):
    client = setup_client
    auth_headers = setup_user

    response = await client.get("api/links")
    assert response.status_code == 401

    response = await client.get("api/links", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_link(setup_client: AsyncClient, setup_user: dict[str, str]):
    client = setup_client
    auth_headers = setup_user

    response = await client.get("api/links/1234567")
    assert response.status_code == 404

    og_link = {"original_url": "http://example.com"}

    response = await client.post("api/links", json=og_link, headers=auth_headers)
    assert response.status_code == 201

    short_key = response.json()["short_key"]

    response = await client.get(f"api/links/{short_key}")
    assert response.status_code == 200
    assert response.json()["original_url"] == og_link["original_url"]
    assert response.json()["short_key"] == short_key


@pytest.mark.asyncio
async def test_delete_link(setup_client: AsyncClient, setup_user: dict[str, str]):
    client = setup_client
    auth_headers = setup_user

    response = await client.delete("api/links/1234567")
    assert response.status_code == 401

    response = await client.delete("api/links/1234567", headers=auth_headers)
    assert response.status_code == 404

    og_link = {"original_url": "http://example.com"}

    response = await client.post("api/links", json=og_link, headers=auth_headers)
    assert response.status_code == 201

    short_key = response.json()["short_key"]

    response = await client.delete(f"api/links/{short_key}", headers=auth_headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_stats_link(setup_client: AsyncClient, setup_user: dict[str, str]):
    client = setup_client
    auth_headers = setup_user

    response = await client.get("api/links/1234567/stats")
    assert response.status_code == 404

    og_link = {"original_url": "http://example.com"}

    response = await client.post("api/links", json=og_link, headers=auth_headers)
    assert response.status_code == 201

    short_key = response.json()["short_key"]

    response = await client.get(f"api/links/{short_key}/stats")
    assert response.status_code == 200
    assert response.json()["short_key"] == short_key
    assert response.json()["original_url"] == og_link["original_url"]
