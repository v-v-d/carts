from dependency_injector import containers, providers

from app.services.items.service import ItemsService
from config import Config
from infra.events.arq import init_arq_redis, ArqTaskProducer
from infra.http.clients.products import ProductsHttpClient
from infra.http.transports.aiohttp import init_aiohttp_transport
from infra.unit_of_work.dummy import Uow


class EventsContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=Config)
    task_broker = providers.Resource(
        init_arq_redis,
        config=config.provided.ARQ_REDIS,
    )
    task_producer = providers.Factory(
        ArqTaskProducer,
        broker=task_broker,
    )


class DBContainer(containers.DeclarativeContainer):
    db = providers.Singleton(dict)
    uow = providers.Factory(Uow, storage=db)


class ProductsClientContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=Config)
    http_transport = providers.Resource(init_aiohttp_transport)
    client = providers.Factory(
        ProductsHttpClient,
        base_url=config.provided.PRODUCTS_CLIENT.base_url,
        transport=http_transport,
    )


class Container(containers.DeclarativeContainer):
    config = Config()

    events = providers.Container(EventsContainer, config=config)
    db = providers.Container(DBContainer)
    products_client = providers.Container(ProductsClientContainer, config=config)

    items_service = providers.Factory(
        ItemsService,
        uow=db.container.uow,
        products_client=products_client.container.client,
    )
