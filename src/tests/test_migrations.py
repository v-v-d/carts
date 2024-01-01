import os
from pathlib import Path

import pytest
from pytest_alembic.tests import (  # noqa
    test_model_definitions_match_ddl,
    test_single_head_revision,
    test_up_down_consistency,
    test_upgrade,
)
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from alembic.config import Config


@pytest.fixture(scope="module")
def alembic_config() -> Config:
    alembic_ini_path = Path(__file__).resolve().parent.parent
    return Config(os.path.join(alembic_ini_path, "alembic.ini"))


@pytest.fixture(scope="module")
async def alembic_engine(sqla_engine: AsyncEngine) -> AsyncConnection:
    async with sqla_engine.connect() as connection:
        yield connection
