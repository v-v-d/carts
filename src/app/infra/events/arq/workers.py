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


def run_worker(worker_settings_path: str) -> None:
    """
    Для корректной работы интеграции arq с Sentry нужно использовать ArqIntegration.
    Эта штука манки патчит внутреннюю логику arq, автоматически оборачивая все задачи и
    cron-джобы в транзакции Sentry. В этих транзакциях также происходит перехват исключений
    и их регистрация в Sentry.

    Важно: Интеграция не будет полноценно работать, если запускать arq-воркер с помощью
    стандартной CLI-команды типа `arq foo.bar.WorkerSettings`, т.к. по непонятным причинам
    нужные патчи не применяются.
    """

    from typing import cast

    import arq
    import sentry_sdk
    from arq.utils import import_string
    from sentry_sdk.integrations.arq import ArqIntegration

    sentry_sdk.init(
        dsn=config.SENTRY.dsn,
        environment="dev",
        traces_sample_rate=0.1,
        enable_tracing=True,
        release="1.0.0",
        integrations=[ArqIntegration()],
    )

    settings_cls = cast("WorkerSettingsType", import_string(worker_settings_path))
    arq.worker.run_worker(settings_cls=settings_cls)
