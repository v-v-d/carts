from contextlib import asynccontextmanager
from typing import AsyncContextManager

import pytest
from typer import Typer
from typer.testing import CliRunner

from app.api.cli.main import app
from app.containers import Container


@pytest.fixture()
def container() -> Container:
    return Container()


@pytest.fixture()
def application(container: Container) -> Typer:
    @asynccontextmanager
    async def _container() -> AsyncContextManager[Container]:
        yield container

    app.container = _container
    return app


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()
