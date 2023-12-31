import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.api.rest.main import app
from app.containers import Container


@pytest.fixture()
def container() -> Container:
    return Container()


@pytest.fixture()
async def application(container: Container) -> FastAPI:
    app.container = container
    return app


@pytest.fixture()
async def http_client(application: FastAPI) -> AsyncClient:
    async with AsyncClient(app=application, base_url="http://test") as client:
        yield client
