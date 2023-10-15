import asyncio
from typing import Any, Generator, Mapping

from aiohttp import (
    ClientConnectionError,
    ClientPayloadError,
    ClientResponse,
    ClientResponseError,
    ClientSession,
)

from app.infra.http.transports.base import HttpTransportError, IHttpTransport


class AioHttpTransport(IHttpTransport):
    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def request(
        self,
        method: str,
        url: str,
        headers: dict[str, Any] | None = None,
        params: Mapping[str, str] | None = None,
        data: dict[Any, Any] | None = None,
    ) -> dict[str, Any] | str:
        try:
            return await self._try_to_make_request(method, url, headers, params, data)
        except (
            ClientConnectionError,
            ClientPayloadError,
            asyncio.TimeoutError,
            BrokenPipeError,
        ) as err:
            raise HttpTransportError(str(err))

    async def _try_to_make_request(
        self,
        method: str,
        url: str,
        headers: dict[str, Any] | None = None,
        params: Mapping[str, str] | None = None,
        data: dict[Any, Any] | None = None,
    ) -> dict[str, Any] | str:
        async with self._session.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data if isinstance(data, str) else None,
            json=data if isinstance(data, (dict, list)) else None,
        ) as response:
            data = await self._get_response_data(response)

            try:
                response.raise_for_status()
            except ClientResponseError as err:
                raise HttpTransportError(data, err.status)

            return data

    async def _get_response_data(self, response: ClientResponse) -> dict[str, Any] | str:
        if response.content_type == "application/json":
            return await response.json()

        return await response.text()


async def init_aiohttp_transport() -> Generator[None, None, AioHttpTransport]:
    session = ClientSession()
    yield AioHttpTransport(session=session)
    await session.close()
