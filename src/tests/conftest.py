import asyncio
from asyncio import AbstractEventLoop

import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Config, DBConfig
from app.infra.repositories.sqla.db import Database
from tests.environment.unit_of_work import TestUow
from tests.utils import apply_migrations, create_database, drop_database


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
async def uow(session_factory: async_sessionmaker[AsyncSession]) -> TestUow:
    return TestUow(session_factory=session_factory)
