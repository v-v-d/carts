import os
from pathlib import Path

import pytest
from _pytest.mark import ParameterSet
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from alembic import command
from alembic.config import Config
from alembic.script import Script, ScriptDirectory

ALEMBIC_INI_PATH = Path(__file__).resolve().parent.parent


def get_alembic_config() -> Config:
    return Config(os.path.join(ALEMBIC_INI_PATH, "alembic.ini"))


def get_revisions_params() -> list[ParameterSet]:
    alembic_cfg = get_alembic_config()
    revisions_dir = ScriptDirectory.from_config(alembic_cfg)
    revisions = list(revisions_dir.walk_revisions("base", "heads"))
    revisions.reverse()

    return [
        pytest.param(
            revision,
            id=revision.path.removeprefix(f"{ALEMBIC_INI_PATH}/alembic/versions/"),
        )
        for revision in revisions
    ]


@pytest.fixture(scope="module")
def alembic_config() -> Config:
    return get_alembic_config()


@pytest.fixture(scope="module")
async def connection(sqla_engine: AsyncEngine) -> AsyncConnection:
    async with sqla_engine.begin() as conn:
        yield conn


@pytest.fixture(scope="module", autouse=True)
async def downgrade_migrations(
    alembic_config: Config,
    connection: AsyncConnection,
) -> None:
    def downgrade_to_base(conn: AsyncConnection) -> None:
        alembic_config.attributes["connection"] = conn
        command.downgrade(alembic_config, "base")

    await connection.run_sync(downgrade_to_base)


@pytest.mark.parametrize("revision", get_revisions_params())
async def test_ok(
    alembic_config: Config,
    revision: Script,
    connection: AsyncConnection,
) -> None:
    def upgrade_and_downgrade(down_revision: str) -> None:
        command.upgrade(alembic_config, revision.revision)
        command.downgrade(alembic_config, down_revision or "-1")
        command.upgrade(alembic_config, revision.revision)

    def check_migration(conn: AsyncConnection) -> None:
        alembic_config.attributes["connection"] = conn

        if isinstance(revision.down_revision, tuple):
            for down_rev in revision.down_revision:
                upgrade_and_downgrade(down_rev)
        else:
            upgrade_and_downgrade(revision.down_revision)

    await connection.run_sync(check_migration)
