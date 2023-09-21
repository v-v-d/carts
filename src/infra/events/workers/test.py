from typing import Any

from arq.connections import RedisSettings

from api import events
from api.events.tasks.test import test_task
from config import Config
from containers import Container
from infra.events.workers.queues import QueueNameEnum

config = Config()


async def startup(ctx: dict[str, Any]) -> None:
    container = Container()
    container.wire(packages=[events.tasks])

    await container.init_resources()

    ctx["container"] = container


async def shutdown(ctx: dict[str, Any]) -> None:
    await ctx["container"].shutdown_resources()


class WorkerSettings:
    redis_settings: RedisSettings = RedisSettings(**config.ARQ_REDIS.model_dump())
    functions = [test_task]
    queue_name = QueueNameEnum.TEST_QUEUE.value
