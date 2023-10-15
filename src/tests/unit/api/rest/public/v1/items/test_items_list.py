from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_asyncio.plugin import SubRequest
from pytest_mock import MockerFixture

from app.api.rest.main import app, lifespan
from app.app_layer.interfaces.services.items.dto import ItemListOutputDTO
from app.app_layer.services.items.items_list import ItemsListService
from tests.utils import fake


@pytest.fixture()
def url_path() -> str:
    return "api/v1/items/"


@pytest.fixture()
def service(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=ItemsListService)

    if "returns" in request.param:
        mock.execute.return_value = request.param["returns"]

    return mock


@pytest.mark.parametrize(
    "service",
    [
        {
            "returns": [
                ItemListOutputDTO(
                    id=fake.numeric.integer_number(start=1),
                    name=fake.text.word(),
                    qty=fake.numeric.integer_number(start=1, end=10),
                    price=fake.numeric.decimal_number(start=1, end=99),
                    cost=fake.numeric.decimal_number(start=1, end=99),
                ),
            ]
        }
    ],
    indirect=True,
)
async def test_ok(http_client: AsyncClient, url_path: str, service: AsyncMock) -> None:
    async with lifespan(app):
        with app.container.items_list_service.override(service):
            response = await http_client.get(url=url_path)

    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json() == [
        {
            "id": service.execute.return_value[0].id,
            "title": service.execute.return_value[0].name,
            "quantity": service.execute.return_value[0].qty,
            "price": service.execute.return_value[0].price,
            "cost": service.execute.return_value[0].cost,
        },
    ]
