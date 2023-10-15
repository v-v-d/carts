from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from pytest_asyncio.plugin import SubRequest
from pytest_mock import MockerFixture

from app.api.rest.main import app, lifespan
from app.api.rest.public.v1.items.errors import ITEM_ADDING_ERROR
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.app_layer.interfaces.repositories.items.exceptions import ItemAlreadyExists
from app.app_layer.interfaces.services.items.dto import ItemAddingInputDTO, ItemAddingOutputDTO
from app.app_layer.services.items.items_adding import ItemsAddingService
from app.domain.items.exceptions import QtyValidationError
from tests.utils import fake


@pytest.fixture()
def url_path() -> str:
    return "api/v1/items/"


@pytest.fixture()
def request_body() -> ItemAddingInputDTO:
    return ItemAddingInputDTO(
        id=fake.numeric.integer_number(start=1),
        qty=fake.numeric.integer_number(start=1, end=10),
    )


@pytest.fixture()
def service(
    request: SubRequest,
    mocker: MockerFixture,
    request_body: ItemAddingInputDTO,
) -> AsyncMock:
    mock = mocker.AsyncMock(spec=ItemsAddingService)

    if "returns" in request.param:
        mock.execute.return_value = request.param["returns"]
    elif "raises" in request.param:
        mock.execute.side_effect = request.param["raises"]

    return mock


@pytest.mark.parametrize(
    "service",
    [
        {
            "returns": ItemAddingOutputDTO(
                id=fake.numeric.integer_number(start=1),
                name=fake.text.word(),
                qty=fake.numeric.integer_number(start=1, end=10),
                price=fake.numeric.decimal_number(start=1, end=99),
                cost=fake.numeric.decimal_number(start=1, end=99),
            ),
        }
    ],
    indirect=True,
)
async def test_ok(
    http_client: AsyncClient,
    url_path: str,
    request_body: ItemAddingInputDTO,
    service: AsyncMock,
) -> None:
    async with lifespan(app):
        with app.container.items_adding_service.override(service):
            response = await http_client.post(url=url_path, content=request_body.model_dump_json())

    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json() == {
        "id": service.execute.return_value.id,
        "title": service.execute.return_value.name,
        "quantity": service.execute.return_value.qty,
        "price": service.execute.return_value.price,
        "cost": service.execute.return_value.cost,
    }


@pytest.mark.parametrize(
    "service",
    [
        pytest.param({"raises": ProductsClientError}, id="products client error"),
        pytest.param({"raises": QtyValidationError}, id="qty validation error"),
        pytest.param({"raises": ItemAlreadyExists}, id="item already exists"),
    ],
    indirect=True,
)
async def test_failed(
    http_client: AsyncClient,
    url_path: str,
    request_body: ItemAddingInputDTO,
    service: AsyncMock,
) -> None:
    async with lifespan(app):
        with app.container.items_adding_service.override(service):
            response = await http_client.post(url=url_path, content=request_body.model_dump_json())

    assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
    assert response.json()["detail"] == ITEM_ADDING_ERROR
