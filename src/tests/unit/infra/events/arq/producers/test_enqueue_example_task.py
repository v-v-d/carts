import asyncio
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from arq.jobs import Job
from redis.asyncio import RedisError

from app.api.events.tasks.example import example_task
from app.app_layer.interfaces.tasks.exceptions import (
    TaskIsNotQueuedError,
    TaskProducingError,
)
from app.infra.events.arq.producers import ArqTaskProducer
from app.infra.events.queues import QueueNameEnum
from tests.utils import fake


@pytest.fixture()
def auth_data() -> str:
    return fake.text.word()


@pytest.fixture()
def expected_broker_call(auth_data: str, cart_id: UUID) -> dict[str, Any]:
    return {
        "function": example_task.__name__,
        "auth_data": auth_data,
        "cart_id": cart_id,
        "_queue_name": QueueNameEnum.EXAMPLE_QUEUE.value,
    }


@pytest.mark.parametrize("broker", [{"returns": AsyncMock(spec=Job)}], indirect=True)
async def test_ok(
    producer: ArqTaskProducer,
    broker: AsyncMock,
    auth_data: str,
    cart_id: UUID,
    expected_broker_call: dict[str, Any],
) -> None:
    await producer.enqueue_example_task(auth_data=auth_data, cart_id=cart_id)
    broker.enqueue_job.assert_awaited_once_with(**expected_broker_call)


@pytest.mark.parametrize("broker", [{"returns": None}], indirect=True)
async def test_not_queued(
    producer: ArqTaskProducer,
    broker: AsyncMock,
    auth_data: str,
    cart_id: UUID,
    expected_broker_call: dict[str, Any],
) -> None:
    with pytest.raises(TaskIsNotQueuedError):
        await producer.enqueue_example_task(auth_data=auth_data, cart_id=cart_id)

    broker.enqueue_job.assert_awaited_once_with(**expected_broker_call)


@pytest.mark.parametrize(
    "broker",
    [
        pytest.param({"raises": ConnectionError("test")}, id="ConnectionError"),
        pytest.param({"raises": OSError("test")}, id="OSError"),
        pytest.param({"raises": RedisError("test")}, id="RedisError"),
        pytest.param({"raises": asyncio.TimeoutError("test")}, id="asyncio.TimeoutError"),
    ],
    indirect=True,
)
async def test_failed(
    producer: ArqTaskProducer,
    broker: AsyncMock,
    auth_data: str,
    cart_id: UUID,
    expected_broker_call: dict[str, Any],
) -> None:
    with pytest.raises(TaskProducingError, match="test"):
        await producer.enqueue_example_task(auth_data=auth_data, cart_id=cart_id)

    broker.enqueue_job.assert_awaited_once_with(**expected_broker_call)
