import pytest
from httpx import AsyncClient

from app.api.rest.main import app


@pytest.fixture()
async def http_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
