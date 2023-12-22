import asyncio
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient, HTTPStatusError
from pytest_asyncio.plugin import SubRequest
from pytest_mock import MockerFixture

from app.infra.http.transports.base import HttpRequestInputDTO, HttpTransportError
from app.infra.http.transports.httpx import HttpxTransport
from tests.utils import fake


@pytest.fixture()
def response(
    request: SubRequest,
    mocker: MockerFixture,
    response_err_text: str,
) -> MagicMock:
    mock = mocker.MagicMock()
    mock.content_type = request.param["Content-Type"]

    if "returns" in request.param:
        if request.param["Content-Type"] == "application/json":
            mock.headers = request.param
            mock.content = str(request.param["returns"])
            mock.json.return_value = request.param["returns"]
        else:
            mock.text = request.param["returns"]

        mock.return_value = request.param["returns"]
    elif "raises" in request.param:
        mock.text = response_err_text
        mock.raise_for_status.side_effect = request.param["raises"]

    return mock


@pytest.fixture()
def client(request: SubRequest, mocker: MockerFixture, response: MagicMock) -> MagicMock:
    mock = mocker.MagicMock(spec=AsyncClient)

    if hasattr(request, "param") and "raises" in request.param:
        mock.request.side_effect = request.param["raises"]
    else:
        mock.request.return_value = response

    return mock


@pytest.fixture()
def transport(client: MagicMock) -> HttpxTransport:
    return HttpxTransport(client=client)


@pytest.mark.parametrize(
    ("request_data", "response"),
    [
        pytest.param(
            HttpRequestInputDTO(
                method=fake.internet.http_method(), url=fake.internet.url()
            ),
            {"Content-Type": "application/json", "returns": {"200": "OK"}},
            id="application/json & method & url",
        ),
        pytest.param(
            HttpRequestInputDTO(
                method=fake.internet.http_method(), url=fake.internet.url()
            ),
            {"Content-Type": "text/html", "returns": "200 OK"},
            id="text/html & method & url",
        ),
        pytest.param(
            HttpRequestInputDTO(
                method=fake.internet.http_method(),
                url=fake.internet.url(),
                headers=fake.internet.http_request_headers(),
            ),
            {"Content-Type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers",
        ),
        pytest.param(
            HttpRequestInputDTO(
                method=fake.internet.http_method(),
                url=fake.internet.url(),
                headers=fake.internet.http_request_headers(),
                params=fake.internet.query_parameters(),
            ),
            {"Content-Type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers & params",
        ),
        pytest.param(
            HttpRequestInputDTO(
                method=fake.internet.http_method(),
                url=fake.internet.url(),
                headers=fake.internet.http_request_headers(),
                params=fake.internet.query_parameters(),
                body=fake.text.word(),
            ),
            {"Content-Type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers & params & data",
        ),
        pytest.param(
            HttpRequestInputDTO(
                method=fake.internet.http_method(),
                url=fake.internet.url(),
                headers=fake.internet.http_request_headers(),
                params=fake.internet.query_parameters(),
                body={"json": "data"},
            ),
            {"Content-Type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers & params & json dict data",
        ),
        pytest.param(
            HttpRequestInputDTO(
                method=fake.internet.http_method(),
                url=fake.internet.url(),
                headers=fake.internet.http_request_headers(),
                params=fake.internet.query_parameters(),
                body=[{"json": "data"}],
            ),
            {"Content-Type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers & params & json list data",
        ),
        pytest.param(
            HttpRequestInputDTO(
                method=fake.internet.http_method(),
                url=fake.internet.url(),
                headers=fake.internet.http_request_headers(),
                params=fake.internet.query_parameters(),
                body="text data",
            ),
            {"Content-Type": "text/html", "returns": "200 OK"},
            id="text/html & method & url & headers & params & text data",
        ),
    ],
    indirect=["response"],
)
async def test_request_ok(
    transport: HttpxTransport,
    request_data: HttpRequestInputDTO,
    response: MagicMock,
    client: MagicMock,
) -> None:
    await transport.request(data=request_data)

    client.request.assert_called_once_with(
        method=request_data.method,
        url=request_data.url,
        headers=request_data.headers,
        params=request_data.params,
        data=request_data.body if isinstance(request_data.body, str) else None,
        json=request_data.body if isinstance(request_data.body, (dict, list)) else None,
    )


@pytest.mark.parametrize(
    ("request_data", "response", "client"),
    [
        pytest.param(
            HttpRequestInputDTO(
                method=fake.internet.http_method(), url=fake.internet.url()
            ),
            {"Content-Type": "text/html", "returns": "200 OK"},
            {"raises": asyncio.TimeoutError},
            id="asyncio.TimeoutError",
        ),
        pytest.param(
            HttpRequestInputDTO(
                method=fake.internet.http_method(), url=fake.internet.url()
            ),
            {"Content-Type": "text/html", "returns": "200 OK"},
            {"raises": BrokenPipeError},
            id="BrokenPipeError",
        ),
    ],
    indirect=["response", "client"],
)
async def test_connection_error(
    transport: HttpxTransport,
    request_data: HttpRequestInputDTO,
    response: MagicMock,
    client: MagicMock,
) -> None:
    with pytest.raises(HttpTransportError):
        await transport.request(data=request_data)

    client.request.assert_called_once_with(
        method=request_data.method,
        url=request_data.url,
        headers=request_data.headers,
        params=request_data.params,
        data=request_data.body if isinstance(request_data.body, str) else None,
        json=request_data.body if isinstance(request_data.body, (dict, list)) else None,
    )


@pytest.mark.parametrize(
    ("request_data", "response"),
    [
        (
            HttpRequestInputDTO(
                method=fake.internet.http_method(), url=fake.internet.url()
            ),
            {
                "Content-Type": "application/json",
                "raises": HTTPStatusError(
                    message="Server error",
                    request=MagicMock(),
                    response=MagicMock(),
                ),
            },
        ),
    ],
    indirect=["response"],
)
async def test_client_response_error(
    transport: HttpxTransport,
    request_data: HttpRequestInputDTO,
    response: MagicMock,
    client: MagicMock,
    response_err_text: str,
) -> None:
    with pytest.raises(
        HttpTransportError,
        match=f"{response.raise_for_status.side_effect} - {response_err_text}",
    ):
        await transport.request(data=request_data)

    client.request.assert_called_once_with(
        method=request_data.method,
        url=request_data.url,
        headers=request_data.headers,
        params=request_data.params,
        data=request_data.body if isinstance(request_data.body, str) else None,
        json=request_data.body if isinstance(request_data.body, (dict, list)) else None,
    )
