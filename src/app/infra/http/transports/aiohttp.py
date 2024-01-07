import asyncio
from logging import DEBUG, getLogger
from types import SimpleNamespace
from typing import Any, Generator

from aiohttp import (
    ClientConnectionError,
    ClientPayloadError,
    ClientResponse,
    ClientResponseError,
    ClientSession,
    TraceConfig,
    TraceRequestEndParams,
    TraceRequestExceptionParams,
    TraceRequestStartParams,
)

from app.infra.http.transports.base import (
    HttpRequestInputDTO,
    HttpTransportConfig,
    HttpTransportError,
    IHttpTransport,
)

logger = getLogger(__name__)


class AioHttpTransport(IHttpTransport):
    """
    Uses the aiohttp library to make HTTP requests asynchronously. It handles
    exceptions that may occur during the request and provides a consistent response
    format.
    """

    def __init__(self, session: ClientSession, config: HttpTransportConfig) -> None:
        self._session = session
        self._config = config

    async def request(self, data: HttpRequestInputDTO) -> dict[str, Any] | str:
        """
        Makes an HTTP request using the provided HttpRequestInputDTO data and returns
        the response data as a dictionary or string.
        """

        try:
            return await self._try_to_make_request(data)
        except (
            ClientConnectionError,
            ClientPayloadError,
            asyncio.TimeoutError,
            BrokenPipeError,
        ) as err:
            raise HttpTransportError(str(err))

    async def _try_to_make_request(
        self, data: HttpRequestInputDTO
    ) -> dict[str, Any] | str:
        trace_ctx = SimpleNamespace(
            data=data, integration_name=self._config.integration_name
        )

        async with self._session.request(
            method=data.method,
            url=data.url,
            headers=data.headers,
            params=data.params,
            data=data.body if isinstance(data.body, str) else None,
            json=data.body if isinstance(data.body, (dict, list)) else None,
            trace_request_ctx=trace_ctx,
        ) as response:
            data = await _get_response_data(response)

            try:
                response.raise_for_status()
            except ClientResponseError as err:
                raise HttpTransportError(message=data, code=err.status)

            return data


async def _get_response_data(response: ClientResponse) -> dict[str, Any] | str:
    if response.content_type == "application/json":
        return await response.json()

    return await response.text()


async def _on_request_start(
    _: ClientSession,
    trace_ctx: SimpleNamespace,
    __: TraceRequestStartParams,
) -> None:
    if logger.getEffectiveLevel() > DEBUG:  # pragma: no cover[coverage err]
        return

    logger.debug("Server make request: %s", vars(trace_ctx.trace_request_ctx))


async def _on_request_end(
    _: ClientSession,
    trace_ctx: SimpleNamespace,
    params: TraceRequestEndParams,
) -> None:
    if logger.getEffectiveLevel() > DEBUG:  # pragma: no cover[coverage err]
        return

    response = await _get_response_data(params.response)
    logger.debug(
        "Server got response: %s. %s", response, vars(trace_ctx.trace_request_ctx)
    )


async def _on_request_exception(
    _: ClientSession,
    trace_ctx: SimpleNamespace,
    params: TraceRequestExceptionParams,
) -> None:
    logger.exception(
        "Server got request error: %s - %s. %s",
        params.exception.__class__.__name__,
        params.exception,
        vars(trace_ctx.trace_request_ctx),
    )


async def init_aiohttp_session_pool() -> Generator[None, None, ClientSession]:
    """
    Initializes and returns an asynchronous HTTP client session with tracing
    capabilities.
    """

    trace_config = TraceConfig()
    trace_config.on_request_start.append(_on_request_start)
    trace_config.on_request_exception.append(_on_request_exception)
    trace_config.on_request_end.append(_on_request_end)

    session = ClientSession(trace_configs=[trace_config])
    yield session
    await session.close()
