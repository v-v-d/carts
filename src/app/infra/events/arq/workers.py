from logging.config import dictConfig
from typing import Any

from arq import cron, func
from arq.connections import RedisSettings

from app.api import events
from app.api.events.tasks.abandoned_carts import (
    process_abandoned_carts,
    send_abandoned_cart_notification,
)
from app.api.events.tasks.example import example_task
from app.config import Config
from app.containers import Container
from app.infra.events.queues import QueueNameEnum
from app.logging import ctx as transaction_ctx
from app.logging import get_logging_config

config = Config()


async def startup(ctx: dict[str, Any]) -> None:
    container = Container()
    container.wire(packages=[events.tasks])

    dictConfig(
        config=get_logging_config(
            transaction_ctx=transaction_ctx,
            config=config.LOGGING,
        ),
    )

    await container.init_resources()

    ctx["container"] = container


async def shutdown(ctx: dict[str, Any]) -> None:
    await ctx["container"].shutdown_resources()


class ConsumerSettings:
    redis_settings: RedisSettings = RedisSettings(**config.ARQ_REDIS.model_dump())
    functions = [
        func(coroutine=example_task, max_tries=config.TASK.max_tries),
        func(coroutine=send_abandoned_cart_notification, max_tries=config.TASK.max_tries),
    ]
    queue_name = QueueNameEnum.EXAMPLE_QUEUE.value
    on_startup = startup
    on_shutdown = shutdown
    keep_result = config.TASK.no_keep_result_value


class PeriodicSettings:
    redis_settings: RedisSettings = RedisSettings(**config.ARQ_REDIS.model_dump())
    cron_jobs = [
        cron(process_abandoned_carts, **config.PERIODIC.schedule),
    ]
    queue_name = QueueNameEnum.PERIODIC_QUEUE.value
    on_startup = startup
    on_shutdown = shutdown
