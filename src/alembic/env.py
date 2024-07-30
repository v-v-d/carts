import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import AsyncConnection

from alembic import context
from app.config import Config
from app.containers import Container
from app.infra.repositories.sqla.db import Database

container = Container()
app_config = Config()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support

from app.infra.repositories.sqla.base import metadata
from app.infra.repositories.sqla.models import *  # noqa

target_metadata = metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

config.set_main_option("sqlalchemy.url", str(app_config.DB.dsn))


def include_name(_name: str, _type: str, parent_names: dict[str, str]) -> bool:
    # useful with 3rd party extensions and their internal schemas and tables

    if "schema_name" not in parent_names:
        return True

    return parent_names["schema_name"] not in (app_config.DB.graph_name, "ag_catalog")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    db: Database = container.db.container.db()

    async with db.engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await db.engine.dispose()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = config.attributes.get("connection", None)

    if isinstance(connectable, AsyncConnection) or connectable is None:
        asyncio.run(run_async_migrations())
    else:
        do_run_migrations(connectable)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
