from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from _pytest.fixtures import SubRequest
from arq import ArqRedis
from pytest_mock import MockerFixture

from app.infra.events.arq.producers import ArqTaskProducer
from tests.utils import fake


@pytest.fixture()
def broker(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=ArqRedis)

    if "returns" in request.param:
        mock.enqueue_job.return_value = request.param["returns"]
    elif "raises" in request.param:
        mock.enqueue_job.side_effect = request.param["raises"]

    return mock


@pytest.fixture()
def producer(broker: AsyncMock) -> ArqTaskProducer:
    return ArqTaskProducer(broker=broker)


@pytest.fixture()
def cart_id() -> UUID:
    return fake.cryptographic.uuid_object()
