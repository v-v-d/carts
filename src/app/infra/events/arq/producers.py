from typing import Generator
from uuid import UUID

from arq import ArqRedis
from arq.connections import RedisSettings, create_pool

from app.app_layer.interfaces.tasks.producer import ITaskProducer
from app.config import ArqRedisConfig
from app.infra.events.queues import QueueNameEnum


class ArqTaskProducer(ITaskProducer):
    def __init__(self, broker: ArqRedis) -> None:
        self._broker = broker

    async def enqueue_example_task(self, auth_data: str, cart_id: UUID) -> None:
        # TODO(me): # circular import :(
        from app.api.events.tasks.example import example_task

        await self._broker.enqueue_job(
            example_task.__name__,
            auth_data=auth_data,
            cart_id=cart_id,
            _queue_name=QueueNameEnum.EXAMPLE_QUEUE.value,
        )

    async def enqueue_abandoned_cart_notification_task(
        self,
        user_id: int,
        cart_id: UUID,
    ) -> None:
        # TODO(me): # circular import :(
        from app.api.events.tasks.abandoned_carts import send_abandoned_cart_notification

        await self._broker.enqueue_job(
            send_abandoned_cart_notification.__name__,
            user_id=user_id,
            cart_id=cart_id,
            _job_id=str(cart_id),
            _queue_name=QueueNameEnum.EXAMPLE_QUEUE.value,
        )


async def init_arq_task_broker(config: ArqRedisConfig) -> Generator[ArqRedis, None, None]:
    pool = await create_pool(RedisSettings(**config.model_dump()))
    yield pool
    await pool.close()
