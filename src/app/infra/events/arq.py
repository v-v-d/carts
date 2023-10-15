from typing import Generator

from arq import ArqRedis
from arq.connections import RedisSettings, create_pool

from app.api.events.tasks.example import example_task
from app.app_layer.interfaces.task_producer import ITaskProducer
from app.config import ArqRedisConfig
from app.infra.events.workers.queues import QueueNameEnum


class ArqTaskProducer(ITaskProducer):
    def __init__(self, broker: ArqRedis) -> None:
        self._broker = broker

    async def enqueue_test_task(self) -> None:
        await self._broker.enqueue_job(
            example_task.__name__,
            _queue_name=QueueNameEnum.TEST_QUEUE.value,
        )


async def init_arq_redis(config: ArqRedisConfig) -> Generator[None, None, ArqRedis]:
    pool = await create_pool(RedisSettings(**config.model_dump()))
    yield pool
    await pool.close()
