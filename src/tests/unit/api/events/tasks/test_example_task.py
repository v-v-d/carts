from typing import Any
from unittest.mock import AsyncMock

import pytest
from pytest_asyncio.plugin import SubRequest
from pytest_mock import MockerFixture

from app.api import events
from app.api.events.tasks.example import example_task
from app.app_layer.interfaces.use_cases.cart_items.dto import AddItemToCartListOutputDTO
from app.app_layer.use_cases.cart_items.items_list import ItemsListUseCase
from app.containers import Container
from tests.utils import fake


@pytest.fixture()
def use_case(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=ItemsListUseCase)

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
    "use_case",
    [
        {
            "returns": [
                AddItemToCartListOutputDTO(
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
async def test_ok(ctx: dict[str, Any], use_case: AsyncMock) -> None:
    container: Container = ctx["container"]

    with container.items_list_use_case.override(use_case):
        await example_task(ctx)

    use_case.execute.assert_awaited_once()
