from contextlib import asynccontextmanager
from types import ModuleType
from typing import AsyncContextManager

from dependency_injector import containers, providers

from app.app_layer.services.items.items_adding import ItemsAddingService
from app.app_layer.services.items.items_list import ItemsListService
from app.config import Config
from app.infra.events.arq import ArqTaskProducer, init_arq_redis
from app.infra.http.clients.products import ProductsHttpClient
from app.infra.http.retry_systems.backoff import BackoffConfig, BackoffRetrySystem
from app.infra.http.transports.aiohttp import init_aiohttp_transport
from app.infra.http.transports.base import HttpTransportConfig, RetryableHttpTransport
from app.infra.repositories.sqla.db import Database
from app.infra.unit_of_work.sqla import Uow


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
    config = providers.Dependency(instance_of=Config)
    db = providers.Singleton(Database, config=config.provided.DB)
    uow = providers.Factory(Uow, session_factory=db.provided.session_factory)


class ProductsClientContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=Config)
    transport = providers.Factory(
        RetryableHttpTransport,
        transport=providers.Resource(
            init_aiohttp_transport,
            config=providers.Factory(
                HttpTransportConfig,
                integration_name=config.provided.PRODUCTS_CLIENT.name,
            ),
        ),
        retry_system=providers.Factory(
            BackoffRetrySystem,
            config=providers.Factory(
                BackoffConfig,
                enabled=config.provided.PRODUCTS_CLIENT.retries_enabled,
            ),
        ),
    )
    client = providers.Factory(
        ProductsHttpClient,
        base_url=config.provided.PRODUCTS_CLIENT.base_url,
        transport=transport,
    )


class Container(containers.DeclarativeContainer):
    config = Config()

    events = providers.Container(EventsContainer, config=config)
    db = providers.Container(DBContainer, config=config)
    products_client = providers.Container(ProductsClientContainer, config=config)

    items_adding_service = providers.Factory(
        ItemsAddingService,
        uow=db.container.uow,
        products_client=products_client.container.client,
    )
    items_list_service = providers.Factory(ItemsListService, uow=db.container.uow)

    @classmethod
    @asynccontextmanager
    async def lifespan(
        cls, wireable_packages: list[ModuleType]
    ) -> AsyncContextManager["Container"]:
        container = cls()
        container.wire(packages=wireable_packages)

        await container.init_resources()

        try:
            yield container
        finally:
            await container.shutdown_resources()
