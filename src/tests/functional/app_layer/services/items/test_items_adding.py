from decimal import Decimal
from http import HTTPMethod, HTTPStatus
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientResponseError
from pytest_asyncio.plugin import SubRequest

from app.app_layer.interfaces.clients.products.client import IProductsClient
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.app_layer.interfaces.services.items.dto import ItemAddingInputDTO
from app.app_layer.interfaces.services.items.items_adding import IItemsAddingService
from app.app_layer.services.items.items_adding import ItemsAddingService
from app.domain.interfaces.repositories.items.exceptions import ItemAlreadyExists
from app.domain.items.entities import Item
from app.domain.items.exceptions import QtyValidationError
from app.infra.http.transports.base import HttpRequestInputDTO, HttpTransportConfig
from tests.environment.unit_of_work import TestUow
from tests.utils import fake

PRODUCTS_CLIENT_RESPONSE = {
    "id": fake.numeric.integer_number(start=1, end=99),
    "title": fake.text.word(),
    "price": fake.numeric.float_number(start=1, end=99, precision=2),
    "description": fake.text.word(),
    "category": fake.text.word(),
    "image": fake.internet.url(),
    "rating": {
        "rate": fake.numeric.float_number(start=1, end=10),
        "count": fake.numeric.integer_number(start=1, end=99),
    },
}


@pytest.fixture()
def service(uow: TestUow, products_client: IProductsClient) -> IItemsAddingService:
    return ItemsAddingService(uow=uow, products_client=products_client)


@pytest.fixture()
def dto(request: SubRequest, item_id: int) -> ItemAddingInputDTO:
    extra_data = request.param if hasattr(request, "param") else {}

    return ItemAddingInputDTO(**{"id": item_id, "qty": 2, **extra_data})


@pytest.fixture()
def expected_products_client_call(
    products_base_url: str,
    item_id: int,
    http_config: HttpTransportConfig,
) -> dict[str, Any]:
    url = f"{products_base_url}products/{item_id}"

    return {
        "method": HTTPMethod.GET,
        "url": url,
        "headers": None,
        "params": None,
        "data": None,
        "json": None,
        "trace_request_ctx": SimpleNamespace(
            data=HttpRequestInputDTO(method=HTTPMethod.GET, url=url),
            integration_name=http_config.integration_name,
        ),
    }


@pytest.mark.parametrize(
    "http_response",
    [{"returns": PRODUCTS_CLIENT_RESPONSE}],
    indirect=True,
)
async def test_ok(
    http_response: AsyncMock,
    http_session: MagicMock,
    uow: TestUow,
    service: IItemsAddingService,
    dto: ItemAddingInputDTO,
    expected_products_client_call: dict[str, Any],
) -> None:
    await service.execute(dto)

    async with uow(autocommit=False):
        items_in_db = await uow.items.get_items()

    assert len(items_in_db) == 1
    assert items_in_db[0].id == dto.id
    assert items_in_db[0].qty == dto.qty
    assert items_in_db[0].name == http_response.json.return_value["title"]
    assert items_in_db[0].price == (
        Decimal(http_response.json.return_value["price"]).quantize(Decimal(".01"))
    )

    http_session.request.assert_called_once_with(**expected_products_client_call)


@pytest.mark.parametrize(
    "http_response",
    [
        {
            "raises": ClientResponseError(
                status=HTTPStatus.SERVICE_UNAVAILABLE,
                request_info=MagicMock(),
                history=MagicMock(),
            ),
        },
    ],
    indirect=True,
)
async def test_products_client_error(
    http_response: AsyncMock,
    http_session: MagicMock,
    response_err_text: str,
    uow: TestUow,
    service: IItemsAddingService,
    dto: ItemAddingInputDTO,
    expected_products_client_call: dict[str, Any],
) -> None:
    with pytest.raises(
        ProductsClientError,
        match=f"{HTTPStatus.SERVICE_UNAVAILABLE} - {response_err_text}",
    ):
        await service.execute(dto)

    async with uow(autocommit=False):
        items_in_db = await uow.items.get_items()

    assert not items_in_db

    http_session.request.assert_called_once_with(**expected_products_client_call)


@pytest.mark.parametrize("http_response", [{"returns": {}}], indirect=True)
async def test_products_client_invalid_response(
    http_response: AsyncMock,
    http_session: MagicMock,
    uow: TestUow,
    service: IItemsAddingService,
    dto: ItemAddingInputDTO,
    expected_products_client_call: dict[str, Any],
) -> None:
    with pytest.raises(
        ProductsClientError,
        match="7 validation errors for ProductOutputDTO",
    ):
        await service.execute(dto)

    async with uow(autocommit=False):
        items_in_db = await uow.items.get_items()

    assert not items_in_db

    http_session.request.assert_called_once_with(**expected_products_client_call)


@pytest.mark.parametrize(
    ("dto", "http_response"),
    [({"qty": Item.min_valid_qty - 1}, {"returns": PRODUCTS_CLIENT_RESPONSE})],
    indirect=True,
)
async def test_invalid_qty(
    http_response: AsyncMock,
    http_session: MagicMock,
    uow: TestUow,
    service: IItemsAddingService,
    dto: ItemAddingInputDTO,
    expected_products_client_call: dict[str, Any],
) -> None:
    with pytest.raises(QtyValidationError):
        await service.execute(dto)

    async with uow(autocommit=False):
        items_in_db = await uow.items.get_items()

    assert not items_in_db

    http_session.request.assert_called_once_with(**expected_products_client_call)


@pytest.mark.usefixtures("existing_item")
@pytest.mark.parametrize(
    "http_response",
    [{"returns": PRODUCTS_CLIENT_RESPONSE}],
    indirect=True,
)
async def test_already_exists(
    http_response: AsyncMock,
    http_session: MagicMock,
    uow: TestUow,
    service: IItemsAddingService,
    dto: ItemAddingInputDTO,
    expected_products_client_call: dict[str, Any],
) -> None:
    with pytest.raises(ItemAlreadyExists):
        await service.execute(dto)

    async with uow(autocommit=False):
        items_in_db = await uow.items.get_items()

    assert len(items_in_db) == 1

    http_session.request.assert_called_once_with(**expected_products_client_call)
