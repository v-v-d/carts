import asyncio
from logging import getLogger
from typing import Generator
from uuid import UUID

from arq import ArqRedis
from arq.connections import RedisSettings, create_pool
from arq.jobs import Job
from redis.asyncio import RedisError

from app.app_layer.interfaces.tasks.exceptions import (
    TaskIsNotQueuedError,
    TaskProducingError,
)
from app.app_layer.interfaces.tasks.producer import ITaskProducer
from app.config import ArqRedisConfig
from app.infra.events.queues import QueueNameEnum

logger = getLogger(__name__)


class ArqTaskProducer(ITaskProducer):
    """
    Responsible for enqueueing different types of tasks using the Arq library. It
    provides methods to enqueue example tasks and abandoned cart notification tasks.
    """

    def __init__(self, broker: ArqRedis) -> None:
        self._broker = broker

    async def enqueue_example_task(self, auth_data: str, cart_id: UUID) -> None:
        """Responsible for enqueueing an example task using the Arq library."""

        # TODO(me): # circular import :(
        from app.api.events.tasks.example import example_task

        await self._enqueue_job(
            function=example_task.__name__,
            auth_data=auth_data,
            cart_id=cart_id,
            _queue_name=QueueNameEnum.EXAMPLE_QUEUE.value,
        )

        logger.debug("Example task for cart %s successfully enqueued!", cart_id)

    async def enqueue_abandoned_cart_notification_task(
        self,
        user_id: int,
        cart_id: UUID,
    ) -> None:
        """
        Responsible for enqueueing an abandoned cart notification task using the
        Arq library. It takes in the user ID and cart ID as inputs and enqueues
        the task with the appropriate parameters.
        """

        # TODO(me): # circular import :(
        from app.api.events.tasks.abandoned_carts import send_abandoned_cart_notification

        try:
            await self._enqueue_job(
                function=send_abandoned_cart_notification.__name__,
                user_id=user_id,
                cart_id=cart_id,
                _job_id=str(cart_id),
                _queue_name=QueueNameEnum.EXAMPLE_QUEUE.value,
            )
        except TaskIsNotQueuedError:
            logger.debug(
                "Failed to enqueue abandoned cart notification task, already queued!"
            )
            return
        except TaskProducingError as err:
            logger.error(
                "Failed to enqueue abandoned cart %s notification task! Error: %s",
                cart_id,
                err,
            )
            raise

        logger.debug(
            "Abandoned cart %s notification task successfully enqueued!", cart_id
        )

    async def _enqueue_job(self, *args, **kwargs) -> Job:
        try:
            job = await self._broker.enqueue_job(*args, **kwargs)
        except (
            ConnectionError,
            OSError,
            RedisError,
            asyncio.TimeoutError,
        ) as err:
            raise TaskProducingError(str(err)) from err

        if job is None:
            raise TaskIsNotQueuedError

        return job


async def init_arq_task_broker(config: ArqRedisConfig) -> Generator[ArqRedis, None, None]:
    """
    Initializes and returns a connection pool to a Redis server using the arq
    library.
    """

    pool = await create_pool(RedisSettings(**config.model_dump()))
    yield pool
    await pool.close()
