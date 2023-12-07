import asyncio
from http import HTTPStatus
from typing import Any
from unittest.mock import MagicMock

import pytest
from aiohttp import ClientConnectionError, ClientPayloadError, ClientResponseError, ClientSession
from pytest_asyncio.plugin import SubRequest
from pytest_mock import MockerFixture

from app.infra.http.transports.aiohttp import AioHttpTransport
from app.infra.http.transports.base import HttpTransportConfig, HttpTransportError
from tests.utils import fake


@pytest.fixture()
def response_err_text() -> str:
    return fake.text.word()


@pytest.fixture()
def response(
    request: SubRequest,
    mocker: MockerFixture,
    response_err_text: str,
) -> MagicMock:
    mock = mocker.MagicMock()
    data_parse_mock = mocker.AsyncMock()

    if "returns" in request.param:
        data_parse_mock.return_value = request.param["returns"]
    elif "raises" in request.param:
        data_parse_mock.return_value = response_err_text
        mock.raise_for_status.side_effect = request.param["raises"]

    mock.content_type = request.param["content_type"]

    if request.param["content_type"] == "application/json":
        mock.json = data_parse_mock
    else:
        mock.text = data_parse_mock

    return mock


@pytest.fixture()
def session(request: SubRequest, mocker: MockerFixture, response: MagicMock) -> MagicMock:
    mock = mocker.MagicMock(spec=ClientSession)

    if hasattr(request, "param") and "raises" in request.param:
        mock.request.side_effect = request.param["raises"]
    else:
        mock.request.return_value.__aenter__.return_value = response

    return mock


@pytest.fixture()
def config() -> HttpTransportConfig:
    return HttpTransportConfig(integration_name="test")


@pytest.fixture()
def transport(session: MagicMock, config: HttpTransportConfig) -> AioHttpTransport:
    return AioHttpTransport(session=session, config=config)


@pytest.mark.parametrize(
    ("request_data", "response"),
    [
        pytest.param(
            {"method": fake.internet.http_method(), "url": fake.internet.url()},
            {"content_type": "application/json", "returns": {"200": "OK"}},
            id="application/json & method & url",
        ),
        pytest.param(
            {"method": fake.internet.http_method(), "url": fake.internet.url()},
            {"content_type": "text/html", "returns": "200 OK"},
            id="text/html & method & url",
        ),
        pytest.param(
            {
                "method": fake.internet.http_method(),
                "url": fake.internet.url(),
                "headers": fake.internet.http_request_headers(),
            },
            {"content_type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers",
        ),
        pytest.param(
            {
                "method": fake.internet.http_method(),
                "url": fake.internet.url(),
                "headers": fake.internet.http_request_headers(),
                "params": fake.internet.query_parameters(),
            },
            {"content_type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers & params",
        ),
        pytest.param(
            {
                "method": fake.internet.http_method(),
                "url": fake.internet.url(),
                "headers": fake.internet.http_request_headers(),
                "params": fake.internet.query_parameters(),
                "data": fake.text.word(),
            },
            {"content_type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers & params & data",
        ),
        pytest.param(
            {
                "method": fake.internet.http_method(),
                "url": fake.internet.url(),
                "headers": fake.internet.http_request_headers(),
                "params": fake.internet.query_parameters(),
                "data": {"json": "data"},
            },
            {"content_type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers & params & json dict data",
        ),
        pytest.param(
            {
                "method": fake.internet.http_method(),
                "url": fake.internet.url(),
                "headers": fake.internet.http_request_headers(),
                "params": fake.internet.query_parameters(),
                "data": [{"json": "data"}],
            },
            {"content_type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers & params & json list data",
        ),
        pytest.param(
            {
                "method": fake.internet.http_method(),
                "url": fake.internet.url(),
                "headers": fake.internet.http_request_headers(),
                "params": fake.internet.query_parameters(),
                "data": "text data",
            },
            {"content_type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers & params & text data",
        ),
    ],
    indirect=["response"],
)
async def test_request_ok(
    transport: AioHttpTransport,
    request_data: dict[str, Any],
    response: MagicMock,
    session: MagicMock,
) -> None:
    await transport.request(**request_data)

    session.request.assert_called_once_with(
        **{
            "headers": None,
            "params": None,
            **request_data,
            "data": request_data["data"]
            if "data" in request_data and isinstance(request_data["data"], str)
            else None,
            "json": request_data["data"]
            if "data" in request_data and isinstance(request_data["data"], (dict, list))
            else None,
        },
    )


@pytest.mark.parametrize(
    ("request_data", "response", "session"),
    [
        pytest.param(
            {"method": fake.internet.http_method(), "url": fake.internet.url()},
            {"content_type": "text/html", "returns": "200 OK"},
            {"raises": ClientConnectionError},
            id="ClientConnectionError",
        ),
        pytest.param(
            {"method": fake.internet.http_method(), "url": fake.internet.url()},
            {"content_type": "text/html", "returns": "200 OK"},
            {"raises": ClientPayloadError},
            id="ClientPayloadError",
        ),
        pytest.param(
            {"method": fake.internet.http_method(), "url": fake.internet.url()},
            {"content_type": "text/html", "returns": "200 OK"},
            {"raises": asyncio.TimeoutError},
            id="asyncio.TimeoutError",
        ),
        pytest.param(
            {"method": fake.internet.http_method(), "url": fake.internet.url()},
            {"content_type": "text/html", "returns": "200 OK"},
            {"raises": BrokenPipeError},
            id="BrokenPipeError",
        ),
    ],
    indirect=["response", "session"],
)
async def test_connection_error(
    transport: AioHttpTransport,
    request_data: dict[str, Any],
    response: MagicMock,
    session: MagicMock,
) -> None:
    with pytest.raises(HttpTransportError):
        await transport.request(**request_data)

    session.request.assert_called_once_with(
        **{
            "headers": None,
            "params": None,
            "data": None,
            "json": None,
            **request_data,
        },
    )


@pytest.mark.parametrize(
    ("request_data", "response"),
    [
        (
            {"method": fake.internet.http_method(), "url": fake.internet.url()},
            {
                "content_type": "application/json",
                "raises": ClientResponseError(
                    status=HTTPStatus.SERVICE_UNAVAILABLE,
                    request_info=MagicMock(),
                    history=MagicMock(),
                ),
            },
        ),
    ],
    indirect=["response"],
)
async def test_client_response_error(
    transport: AioHttpTransport,
    request_data: dict[str, Any],
    response: MagicMock,
    session: MagicMock,
    response_err_text: str,
) -> None:
    with pytest.raises(
        HttpTransportError,
        match=f"{HTTPStatus.SERVICE_UNAVAILABLE} - {response_err_text}",
    ):
        await transport.request(**request_data)

    session.request.assert_called_once_with(
        **{
            "headers": None,
            "params": None,
            "data": None,
            "json": None,
            **request_data,
        },
    )
