import asyncio
import pytest


@pytest.mark.asyncio
async def test_health(setup_client):
    client = setup_client

    response = await client.get("api/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_with_error(setup_client, monkeypatch: pytest.MonkeyPatch):
    client = setup_client

    async def wait_for(fut, timeout):
        fut.close()  # omit "coroutine was never awaited"
        raise asyncio.TimeoutError

    monkeypatch.setattr("shortly.api.health.asyncio.wait_for", wait_for)

    response = await client.get("api/health")
    assert response.status_code == 503
