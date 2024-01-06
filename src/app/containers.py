from contextlib import asynccontextmanager
from types import ModuleType
from typing import AsyncContextManager

from dependency_injector import containers, providers

from app.app_layer.use_cases.abandoned_carts_service import AbandonedCartsService
from app.app_layer.use_cases.cart_config.service import CartConfigService
from app.app_layer.use_cases.cart_items.add_item import AddCartItemUseCase
from app.app_layer.use_cases.cart_items.delete_item import DeleteCartItemUseCase
from app.app_layer.use_cases.cart_items.update_item import UpdateCartItemUseCase
from app.app_layer.use_cases.carts.cart_apply_coupon import CartApplyCouponUseCase
from app.app_layer.use_cases.carts.cart_complete import CompleteCartUseCase
from app.app_layer.use_cases.carts.cart_delete import CartDeleteUseCase
from app.app_layer.use_cases.carts.cart_list import CartListUseCase
from app.app_layer.use_cases.carts.cart_lock import LockCartUseCase
from app.app_layer.use_cases.carts.cart_remove_coupon import CartRemoveCouponUseCase
from app.app_layer.use_cases.carts.cart_retrieve import CartRetrieveUseCase
from app.app_layer.use_cases.carts.cart_unlock import UnlockCartUseCase
from app.app_layer.use_cases.carts.clear_cart import ClearCartUseCase
from app.app_layer.use_cases.carts.create_cart import CreateCartUseCase
from app.config import Config
from app.infra.auth_system import FakeJWTAuthSystem
from app.infra.events.arq.producers import ArqTaskProducer, init_arq_task_broker
from app.infra.http.clients.coupons import CouponsHttpClient
from app.infra.http.clients.notifications import NotificationsHttpClient
from app.infra.http.clients.products import ProductsHttpClient
from app.infra.http.retry_systems.backoff import BackoffConfig, BackoffRetrySystem
from app.infra.http.transports.aiohttp import AioHttpTransport, init_aiohttp_session_pool
from app.infra.http.transports.base import HttpTransportConfig, RetryableHttpTransport
from app.infra.redis_lock_system import RedisLockSystem, init_redis
from app.infra.repositories.sqla.db import Database
from app.infra.unit_of_work.sqla import Uow


class EventsContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=Config)
    broker = providers.Resource(init_arq_task_broker, config=config.provided.ARQ_REDIS)
    task_producer = providers.Factory(ArqTaskProducer, broker=broker)


class DBContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=Config)
    db = providers.Singleton(Database, config=config.provided.DB)
    uow = providers.Factory(Uow, session_factory=db.provided.session_factory)


class ProductsClientContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=Config)
    transport = providers.Factory(
        RetryableHttpTransport,
        transport=providers.Factory(
            AioHttpTransport,
            session=providers.Resource(init_aiohttp_session_pool),
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


class CouponsClientContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=Config)
    transport = providers.Factory(
        RetryableHttpTransport,
        transport=providers.Factory(
            AioHttpTransport,
            session=providers.Resource(init_aiohttp_session_pool),
            config=providers.Factory(
                HttpTransportConfig,
                integration_name=config.provided.COUPONS_CLIENT.name,
            ),
        ),
        retry_system=providers.Factory(
            BackoffRetrySystem,
            config=providers.Factory(
                BackoffConfig,
                enabled=config.provided.COUPONS_CLIENT.retries_enabled,
            ),
        ),
    )
    client = providers.Factory(
        CouponsHttpClient,
        base_url=config.provided.COUPONS_CLIENT.base_url,
        transport=transport,
    )


class NotificationsClientContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=Config)
    transport = providers.Factory(
        RetryableHttpTransport,
        transport=providers.Factory(
            AioHttpTransport,
            session=providers.Resource(init_aiohttp_session_pool),
            config=providers.Factory(
                HttpTransportConfig,
                integration_name=config.provided.NOTIFICATIONS_CLIENT.name,
            ),
        ),
        retry_system=providers.Factory(
            BackoffRetrySystem,
            config=providers.Factory(
                BackoffConfig,
                enabled=config.provided.NOTIFICATIONS_CLIENT.retries_enabled,
            ),
        ),
    )
    client = providers.Factory(
        NotificationsHttpClient,
        base_url=config.provided.NOTIFICATIONS_CLIENT.base_url,
        transport=transport,
    )


class DistributedLockSystemContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=Config)
    redis = providers.Resource(
        init_redis,
        config=config.provided.REDIS_LOCK,
    )
    system = providers.Factory(
        RedisLockSystem,
        redis=redis,
        config=config.provided.REDIS_LOCK,
    )


class Container(containers.DeclarativeContainer):
    config = Config()

    events = providers.Container(EventsContainer, config=config)
    db = providers.Container(DBContainer, config=config)
    products_client = providers.Container(ProductsClientContainer, config=config)
    coupons_client = providers.Container(CouponsClientContainer, config=config)
    notifications_client = providers.Container(
        NotificationsClientContainer, config=config
    )
    auth_system = providers.Factory(FakeJWTAuthSystem)
    distributed_lock_system = providers.Container(
        DistributedLockSystemContainer,
        config=config,
    )

    create_cart_use_case = providers.Factory(
        CreateCartUseCase, uow=db.container.uow, auth_system=auth_system
    )
    cart_retrieve_use_case = providers.Factory(
        CartRetrieveUseCase,
        uow=db.container.uow,
        auth_system=auth_system,
    )
    cart_delete_use_case = providers.Factory(
        CartDeleteUseCase,
        uow=db.container.uow,
        auth_system=auth_system,
        distributed_lock_system=distributed_lock_system.container.system,
    )

    add_cart_item_use_case = providers.Factory(
        AddCartItemUseCase,
        uow=db.container.uow,
        products_client=products_client.container.client,
        auth_system=auth_system,
        distributed_lock_system=distributed_lock_system.container.system,
    )
    update_cart_item_use_case = providers.Factory(
        UpdateCartItemUseCase,
        uow=db.container.uow,
        auth_system=auth_system,
        distributed_lock_system=distributed_lock_system.container.system,
    )
    delete_cart_item_use_case = providers.Factory(
        DeleteCartItemUseCase,
        uow=db.container.uow,
        auth_system=auth_system,
        distributed_lock_system=distributed_lock_system.container.system,
    )
    clear_cart_use_case = providers.Factory(
        ClearCartUseCase,
        uow=db.container.uow,
        auth_system=auth_system,
        distributed_lock_system=distributed_lock_system.container.system,
    )

    cart_apply_coupon_use_case = providers.Factory(
        CartApplyCouponUseCase,
        uow=db.container.uow,
        coupons_client=coupons_client.container.client,
        auth_system=auth_system,
        distributed_lock_system=distributed_lock_system.container.system,
    )
    cart_remove_coupon_use_case = providers.Factory(
        CartRemoveCouponUseCase,
        uow=db.container.uow,
        auth_system=auth_system,
        distributed_lock_system=distributed_lock_system.container.system,
    )

    lock_cart_use_case = providers.Factory(
        LockCartUseCase,
        uow=db.container.uow,
        distributed_lock_system=distributed_lock_system.container.system,
    )
    unlock_cart_use_case = providers.Factory(
        UnlockCartUseCase,
        uow=db.container.uow,
        distributed_lock_system=distributed_lock_system.container.system,
    )
    complete_cart_use_case = providers.Factory(
        CompleteCartUseCase,
        uow=db.container.uow,
        distributed_lock_system=distributed_lock_system.container.system,
    )
    cart_list_use_case = providers.Factory(
        CartListUseCase,
        uow=db.container.uow,
        auth_system=auth_system,
    )
    cart_config_service = providers.Factory(
        CartConfigService,
        uow=db.container.uow,
        auth_system=auth_system,
    )
    abandoned_carts_service = providers.Factory(
        AbandonedCartsService,
        uow=db.container.uow,
        task_producer=events.container.task_producer,
        notification_client=notifications_client.container.client,
        config=config.TASK,
    )

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
