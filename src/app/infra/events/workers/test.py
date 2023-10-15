from typing import Any

from arq.connections import RedisSettings

from app.api import events
from app.api.events.tasks.test import test_task
from app.config import Config
from app.containers import Container
from app.infra.events.workers.queues import QueueNameEnum

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
