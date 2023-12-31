from unittest.mock import AsyncMock

import pytest
from arq import ArqRedis
from pytest_mock import MockerFixture

from app.api.events.tasks.example import example_task
from app.infra.events.arq.producers import ArqTaskProducer
from app.infra.events.queues import QueueNameEnum
from tests.utils import fake


@pytest.fixture()
def broker(mocker: MockerFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=ArqRedis)


@pytest.fixture()
def task_producer(broker: AsyncMock) -> ArqTaskProducer:
    return ArqTaskProducer(broker=broker)


async def test_enqueue_example_task_ok(
    task_producer: ArqTaskProducer,
    broker: AsyncMock,
) -> None:
    task_kwargs = {
        "auth_data": fake.text.word(),
        "cart_id": fake.cryptographic.uuid_object(),
    }
    await task_producer.enqueue_example_task(**task_kwargs)

    broker.enqueue_job.assert_awaited_once_with(
        example_task.__name__,
        **task_kwargs,
        _queue_name=QueueNameEnum.EXAMPLE_QUEUE.value,
    )
