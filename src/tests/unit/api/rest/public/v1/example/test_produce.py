from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from _pytest.fixtures import SubRequest
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app import api
from app.app_layer.interfaces.tasks.producer import ITaskProducer
from app.containers import Container
from tests.utils import fake


@pytest.fixture()
def container() -> Container:
    container = Container()
    container.wire(packages=[api.rest.public.v1.example])

    return container


@pytest.fixture()
def url_path() -> str:
    return "api/v1/example/produce"


@pytest.fixture()
def task_producer(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=ITaskProducer)

    if "returns" in request.param:
        mock.enqueue_example_task.return_value = request.param["returns"]
    elif "raises" in request.param:
        mock.enqueue_example_task.side_effect = request.param["raises"]

    return mock


@pytest.fixture()
def application(application: FastAPI, task_producer: AsyncMock) -> FastAPI:
    with application.container.events.task_producer.override(task_producer):
        yield application


@pytest.mark.parametrize("task_producer", [{"returns": None}], indirect=True)
async def test_ok(
    http_client: AsyncClient, task_producer: AsyncMock, url_path: str
) -> None:
    response = await http_client.post(url=url_path, json=fake.cryptographic.uuid())
    assert response.status_code == HTTPStatus.ACCEPTED, response.text
