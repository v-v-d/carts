from dependency_injector import containers, providers

from config import Config
from infra.events.arq import init_arq_redis, ArqTaskProducer


class Container(containers.DeclarativeContainer):
    config = Config()

    task_broker = providers.Resource(
        init_arq_redis,
        config=config.ARQ_REDIS,
    )
    task_producer = providers.Factory(
        ArqTaskProducer,
        broker=task_broker,
    )
