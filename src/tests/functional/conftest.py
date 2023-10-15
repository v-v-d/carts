from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientSession
from pytest_asyncio.plugin import SubRequest
from pytest_mock import MockerFixture

from app.app_layer.interfaces.clients.products.client import IProductsClient
from app.infra.http.clients.products import ProductsHttpClient
from app.infra.http.transports.aiohttp import AioHttpTransport
from app.infra.http.transports.base import IHttpTransport
from tests.utils import fake


@pytest.fixture()
def products_base_url() -> str:
    return fake.internet.url()


@pytest.fixture()
def response_err_text() -> str:
    return fake.text.word()


@pytest.fixture()
def http_response(
    request: SubRequest,
    mocker: MockerFixture,
    response_err_text: str,
) -> AsyncMock:
    mock = mocker.MagicMock()
    data_parse_mock = mocker.AsyncMock()

    if "returns" in request.param:
        mock.content_type = "application/json"
        data_parse_mock.return_value = request.param["returns"]
        mock.json = data_parse_mock
    elif "raises" in request.param:
        mock.content_type = "text/html"
        data_parse_mock.return_value = response_err_text
        mock.text = data_parse_mock
        mock.raise_for_status.side_effect = request.param["raises"]

    return mock


@pytest.fixture()
def http_session(mocker: MockerFixture, http_response: AsyncMock) -> MagicMock:
    mock = mocker.MagicMock(spec=ClientSession)
    mock.request.return_value.__aenter__.return_value = http_response

    return mock


@pytest.fixture()
def products_transport(http_session: AsyncMock) -> IHttpTransport:
    return AioHttpTransport(session=http_session)


@pytest.fixture()
def products_client(products_base_url: str, products_transport: IHttpTransport) -> IProductsClient:
    return ProductsHttpClient(base_url=products_base_url, transport=products_transport)
