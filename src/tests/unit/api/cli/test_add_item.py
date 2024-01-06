from unittest.mock import AsyncMock

import pytest
from _pytest.fixtures import SubRequest
from pytest_mock import MockerFixture
from typer import Typer
from typer.testing import CliRunner

from app import api
from app.app_layer.use_cases.cart_items.add_item import AddCartItemUseCase
from app.app_layer.use_cases.carts.dto import CartOutputDTO, ItemOutputDTO
from app.containers import Container
from app.domain.carts.value_objects import CartStatusEnum
from tests.utils import fake


@pytest.fixture()
def use_case(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=AddCartItemUseCase)

    if "returns" in request.param:
        mock.execute.return_value = request.param["returns"]
    elif "raises" in request.param:
        mock.execute.side_effect = request.param["raises"]

    return mock


@pytest.fixture()
def container(use_case: AsyncMock) -> Container:
    container = Container()
    container.wire(packages=[api.cli.items])

    with container.add_cart_item_use_case.override(use_case):
        yield container


@pytest.mark.parametrize(
    "use_case",
    [
        {
            "returns": CartOutputDTO(
                created_at=fake.datetime.datetime(),
                id=fake.cryptographic.uuid_object(),
                user_id=fake.numeric.integer_number(start=1),
                status=CartStatusEnum.OPENED,
                items=[
                    ItemOutputDTO(
                        id=fake.numeric.integer_number(start=1),
                        name=fake.text.word(),
                        qty=fake.numeric.integer_number(start=1),
                        price=fake.numeric.integer_number(start=1),
                        cost=fake.numeric.integer_number(start=1),
                        is_weight=fake.random.choice([False, True]),
                    ),
                ],
                items_qty=0,
                cost=0,
                checkout_enabled=False,
                coupon=None,
            ),
        }
    ],
    indirect=True,
)
def test_ok(application: Typer, runner: CliRunner, use_case: AsyncMock) -> None:
    result = runner.invoke(
        application,
        ["add-item", "1", "1", "bbd90be1-8b74-4721-a3a3-ebe0e6c5c292", "Bearer admin.1"],
    )
    assert result.exit_code == 0
