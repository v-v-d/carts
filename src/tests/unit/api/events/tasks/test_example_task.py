from typing import Any
from unittest.mock import AsyncMock

import pytest
from pytest_asyncio.plugin import SubRequest
from pytest_mock import MockerFixture

from app.api import events
from app.api.events.tasks.example import example_task
from app.app_layer.interfaces.services.items.dto import ItemListOutputDTO
from app.app_layer.services.items.items_list import ItemsListService
from app.containers import Container
from tests.utils import fake


@pytest.fixture()
def service(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=ItemsListService)

    if "returns" in request.param:
        mock.execute.return_value = request.param["returns"]

    return mock


@pytest.fixture()
def container() -> Container:
    container = Container()
    container.wire(packages=[events.tasks])

    return container


@pytest.fixture()
def ctx(container: Container) -> dict[str, Any]:
    return {"container": container}


@pytest.mark.parametrize(
    "service",
    [
        {
            "returns": [
                ItemListOutputDTO(
                    id=fake.numeric.integer_number(start=1),
                    name=fake.text.word(),
                    qty=fake.numeric.decimal_number(start=1),
                    price=fake.numeric.decimal_number(start=1),
                    cost=fake.numeric.decimal_number(start=1),
                ),
            ]
        },
    ],
    indirect=True,
)
async def test_ok(ctx: dict[str, Any], service: AsyncMock) -> None:
    container: Container = ctx["container"]

    with container.items_list_service.override(service):
        await example_task(ctx)

    service.execute.assert_awaited_once()
