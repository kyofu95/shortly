import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient

from shortly.core.database import async_engine
from shortly.models.base import Base
from shortly.models.user import User
from shortly.models.link import Link
from shortly.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield None

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def setup_client(setup_db):
    """Global app fixture."""
    async with AsyncClient(app=app, base_url="http://localhost") as client:
        yield client
