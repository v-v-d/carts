import asyncio
from asyncio import AbstractEventLoop
from decimal import Decimal

import pytest
from _pytest.fixtures import SubRequest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Config, DBConfig
from app.domain.cart_config.dto import CartConfigDTO
from app.domain.cart_config.entities import CartConfig
from app.domain.cart_coupons.dto import CartCouponDTO
from app.domain.cart_coupons.entities import CartCoupon
from app.domain.cart_items.dto import ItemDTO
from app.domain.cart_items.entities import CartItem
from app.domain.carts.dto import CartDTO
from app.domain.carts.entities import Cart
from app.domain.carts.value_objects import CartStatusEnum
from app.infra.repositories.sqla.db import Database
from tests.utils import apply_migrations, create_database, drop_database, fake


@pytest.fixture(scope="session")
def config() -> Config:
    return Config()


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    """Creates an instance of the default event loop for each test case."""

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_config(event_loop: AbstractEventLoop, config: Config) -> DBConfig:
    return config.DB.model_copy(update={"dsn": str(config.DB.dsn) + "_test"})


@pytest.fixture(scope="session")
async def database(
    event_loop: AbstractEventLoop,
    db_config: DBConfig,
) -> None:
    await create_database(db_config.dsn)
    engine = create_async_engine(db_config.dsn, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(apply_migrations)

    await engine.dispose()

    try:
        yield
    finally:
        await drop_database(db_config.dsn)


@pytest.fixture(scope="session")
async def sqla_database(db_config: DBConfig, database: None) -> Database:
    return Database(db_config)


@pytest.fixture(scope="session")
async def sqla_engine(sqla_database: Database) -> AsyncEngine:
    yield sqla_database.engine
    await sqla_database.engine.dispose()


@pytest.fixture()
async def session_factory(
    sqla_engine: AsyncEngine,
    sqla_database: Database,
) -> async_sessionmaker[AsyncSession]:
    """
    Fixture that returns a SQLAlchemy sessionmaker with a SAVEPOINT, and the rollback to it
    after the test completes.
    """

    connection = await sqla_engine.connect()
    trans = await connection.begin()

    yield async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    await trans.rollback()
    await connection.close()


@pytest.fixture()
async def cart_config(request: SubRequest) -> CartConfig:
    extra_data = getattr(request, "param", {})

    return CartConfig(
        data=CartConfigDTO(
            **{
                "max_items_qty": fake.numeric.integer_number(start=2),
                "min_cost_for_checkout": fake.numeric.integer_number(start=1),
                "limit_items_by_id": {},
                "hours_since_update_until_abandoned": fake.numeric.integer_number(
                    start=1
                ),
                "max_abandoned_notifications_qty": fake.numeric.integer_number(start=1),
                "abandoned_cart_text": fake.text.word(),
                **extra_data,
            },
        ),
    )


@pytest.fixture()
async def cart(request: SubRequest, cart_config: CartConfig) -> Cart:
    extra_data = getattr(request, "param", {})

    return Cart(
        data=CartDTO(
            **{
                "created_at": fake.datetime.datetime(),
                "id": fake.cryptographic.uuid_object(),
                "user_id": fake.numeric.integer_number(start=1),
                "status": CartStatusEnum.OPENED,
                **extra_data,
            },
        ),
        items=[],
        config=cart_config,
    )


@pytest.fixture()
async def cart_item(request: SubRequest, cart: Cart, cart_config: CartConfig) -> CartItem:
    extra_data = getattr(request, "param", {})

    return CartItem(
        data=ItemDTO(
            **{
                "id": fake.numeric.integer_number(start=1),
                "name": fake.text.word(),
                "qty": fake.numeric.integer_number(
                    start=1,
                    end=cart_config.max_items_qty,
                ),
                "price": fake.numeric.decimal_number(start=1).quantize(Decimal(".00")),
                "is_weight": fake.choice.choice([True, False]),
                "cart_id": cart.id,
                **extra_data,
            },
        ),
    )


@pytest.fixture()
async def coupon(request: SubRequest, cart: Cart) -> CartCoupon:
    extra_data = getattr(request, "param", {})

    return CartCoupon(
        cart=cart,
        data=CartCouponDTO(
            **{
                "coupon_id": fake.text.word(),
                "min_cart_cost": fake.numeric.decimal_number(start=1),
                "discount_abs": fake.numeric.decimal_number(start=1),
                **extra_data,
            },
        ),
    )
