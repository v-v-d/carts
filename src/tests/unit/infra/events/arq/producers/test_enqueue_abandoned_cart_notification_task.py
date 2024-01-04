import asyncio
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from arq.jobs import Job
from redis.asyncio import RedisError

from app.api.events.tasks.abandoned_carts import send_abandoned_cart_notification
from app.app_layer.interfaces.tasks.exceptions import TaskProducingError
from app.infra.events.arq.producers import ArqTaskProducer
from app.infra.events.queues import QueueNameEnum
from tests.utils import fake


@pytest.fixture()
def user_id() -> int:
    return fake.numeric.integer_number(start=1)


@pytest.fixture()
def expected_broker_call(user_id: int, cart_id: UUID) -> dict[str, Any]:
    return {
        "function": send_abandoned_cart_notification.__name__,
        "user_id": user_id,
        "cart_id": cart_id,
        "_job_id": str(cart_id),
        "_queue_name": QueueNameEnum.EXAMPLE_QUEUE.value,
    }


@pytest.mark.parametrize(
    "broker",
    [
        pytest.param({"returns": AsyncMock(spec=Job)}, id="successfully enqueued"),
        pytest.param({"returns": None}, id="already enqueued"),
    ],
    indirect=True,
)
async def test_ok(
    producer: ArqTaskProducer,
    broker: AsyncMock,
    user_id: int,
    cart_id: UUID,
    expected_broker_call: dict[str, Any],
) -> None:
    await producer.enqueue_abandoned_cart_notification_task(
        user_id=user_id,
        cart_id=cart_id,
    )
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
    user_id: int,
    cart_id: UUID,
    expected_broker_call: dict[str, Any],
) -> None:
    with pytest.raises(TaskProducingError, match="test"):
        await producer.enqueue_abandoned_cart_notification_task(
            user_id=user_id,
            cart_id=cart_id,
        )

    broker.enqueue_job.assert_awaited_once_with(**expected_broker_call)
