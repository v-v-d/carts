import json
from collections.abc import Callable
from typing import Any

import orjson
from pydantic.v1.json import pydantic_encoder
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import DBConfig


def json_dumps(value: Any, *, default: Callable[[Any], Any] = pydantic_encoder) -> str:
    return json.dumps(value, default=default)


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

                    # useful with 3rd party extensions and their internal schemas and tables
                    "options": "-c search_path=ag_catalog,content,public",
                },
            },
            json_serializer=json_dumps,
            json_deserializer=orjson.loads,
            echo=config.debug,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory
