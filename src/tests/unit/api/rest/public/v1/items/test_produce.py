from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app.api.rest.main import app, lifespan
from app.infra.events.arq import ArqTaskProducer


@pytest.fixture()
def url_path() -> str:
    return "api/v1/cart_items/produce"


@pytest.fixture()
def task_producer(mocker: MockerFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=ArqTaskProducer)


async def test_ok(
    http_client: AsyncClient, url_path: str, task_producer: AsyncMock
) -> None:
    async with lifespan(app):
        with app.container.events.task_producer.override(task_producer):
            response = await http_client.post(url=url_path)

    assert response.status_code == HTTPStatus.ACCEPTED, response.text
