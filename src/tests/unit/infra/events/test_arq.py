from unittest.mock import AsyncMock

import pytest
from arq import ArqRedis
from pytest_mock import MockerFixture

from app.api.events.tasks.example import example_task
from app.infra.events.arq.producer import ArqTaskProducer
from app.infra.events.queues import QueueNameEnum


@pytest.fixture()
def broker(mocker: MockerFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=ArqRedis)


@pytest.fixture()
def task_producer(broker: AsyncMock) -> ArqTaskProducer:
    return ArqTaskProducer(broker)


async def test_enqueue_test_task_ok(
    task_producer: ArqTaskProducer,
    broker: AsyncMock,
) -> None:
    await task_producer.enqueue_example_task()

    broker.enqueue_job.assert_awaited_once_with(
        example_task.__name__,
        _queue_name=QueueNameEnum.EXAMPLE_QUEUE.value,
    )
