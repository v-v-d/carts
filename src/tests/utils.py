import os
from pathlib import Path
from typing import Optional

import mimesis
from mimesis.enums import Locale
from sqlalchemy import URL, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from alembic import command
from alembic.config import Config


class FakeGeneric(mimesis.Generic):
    """
    Custom class inherited from the mimesis.Generic and made for type hints only,
    because of mimesis.Generic set attributes dynamically for lazy initialization.
    """

    address: Optional[mimesis.Address]
    binaryfile: Optional[mimesis.BinaryFile]
    finance: Optional[mimesis.Finance]
    choice: Optional[mimesis.Choice]
    code: Optional[mimesis.Code]
    datetime: Optional[mimesis.Datetime]
    development: Optional[mimesis.Development]
    file: Optional[mimesis.File]  # noqa: VNE002
    food: Optional[mimesis.Food]
    hardware: Optional[mimesis.Hardware]
    internet: Optional[mimesis.Internet]
    numeric: Optional[mimesis.Numeric]
    path: Optional[mimesis.Path]
    payment: Optional[mimesis.Payment]
    person: Optional[mimesis.Person]
    science: Optional[mimesis.Science]
    text: Optional[mimesis.Text]
    transport: Optional[mimesis.Transport]
    cryptographic: Optional[mimesis.Cryptographic]


fake = FakeGeneric(locale=Locale.RU)

POSTGRES_DEFAULT_DB = "postgres"


def apply_migrations(connection: AsyncConnection) -> None:
    base_dir = Path(__file__).resolve().parent.parent
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))

    alembic_cfg.attributes["connection"] = connection
    command.upgrade(alembic_cfg, "head")


async def create_database(url: str) -> None:
    url_object = make_url(url)
    database_name = url_object.database
    dbms_url = url_object.set(database=POSTGRES_DEFAULT_DB)
    engine = create_async_engine(dbms_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'")
        )
        database_exists = result.scalar() == 1

    if database_exists:
        await drop_database(url_object)

    async with engine.connect() as conn:
        await conn.execute(
            text(f'CREATE DATABASE "{database_name}" ENCODING "utf8" TEMPLATE template1')
        )
    await engine.dispose()


async def drop_database(url: URL) -> None:
    url_object = make_url(url)
    dbms_url = url_object.set(database=POSTGRES_DEFAULT_DB)
    engine = create_async_engine(dbms_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        disc_users = """
        SELECT pg_terminate_backend(pg_stat_activity.%(pid_column)s)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '%(database)s'
          AND %(pid_column)s <> pg_backend_pid();
        """ % {
            "pid_column": "pid",
            "database": url_object.database,
        }
        await conn.execute(text(disc_users))

        await conn.execute(text(f'DROP DATABASE "{url_object.database}"'))
