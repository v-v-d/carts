from collections.abc import Callable
from typing import Any

import orjson
from pydantic.json import pydantic_encoder
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import DBConfig


def orjson_dumps(value: Any, *, default: Callable[[Any], Any] = pydantic_encoder) -> str:
    return orjson.dumps(value, default=default).decode()


class Database:
    def __init__(self, config: DBConfig) -> None:
        self._engine: AsyncEngine = create_async_engine(
            url=str(config.dsn),
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_pre_ping=config.pool_pre_ping,
            connect_args={
                "timeout": config.connection_timeout,
                "command_timeout": config.command_timeout,
                **config.connect_args,
                "server_settings": {
                    # disable extra statement "WITH RECURSIVE typeinfo_tree ..." see
                    # https://github.com/MagicStack/asyncpg/issues/530
                    "jit": "off",
                    **config.server_settings,
                    "application_name": config.app_name,
                    "timezone": config.timezone,
                },
            },
            json_serializer=orjson_dumps,
            json_deserializer=orjson.loads,
        )
        self._session_factory = async_sessionmaker(bind=self._engine, expire_on_commit=False)

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory
