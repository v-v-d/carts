from typing import Any
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.api.rest.main import app
from app.containers import Container
from tests.utils import fake


@pytest.fixture()
def container() -> Container:
    return Container()


@pytest.fixture()
async def application(container: Container) -> FastAPI:
    app.container = container
    return app


@pytest.fixture()
async def headers() -> dict[str, Any]:
    return {"Authorization": fake.internet.http_request_headers()["Authorization"]}


@pytest.fixture()
async def http_client(application: FastAPI, headers: dict[str, Any]) -> AsyncClient:
    async with AsyncClient(
        app=application,
        base_url="http://test",
        headers=headers,
    ) as client:
        yield client


@pytest.fixture()
def cart_id() -> UUID:
    return fake.cryptographic.uuid_object()
