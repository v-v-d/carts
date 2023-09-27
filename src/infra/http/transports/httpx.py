import asyncio
from typing import Any, Mapping, Generator

from httpx import AsyncClient, HTTPError, Response

from infra.http.transports.base import IHttpTransport, HttpTransportError


class HttpxTransport(IHttpTransport):
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

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
        except (asyncio.TimeoutError, BrokenPipeError) as err:
            raise HttpTransportError(str(err))

    async def _try_to_make_request(
        self,
        method: str,
        url: str,
        headers: dict[str, Any] | None = None,
        params: Mapping[str, str] | None = None,
        data: dict[Any, Any] | None = None,
    ) -> dict[str, Any] | str:
        response = await self._client.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data if isinstance(data, str) else None,
            json=data if isinstance(data, (dict, list)) else None,
        )

        data = await self._get_response_data(response)

        try:
            response.raise_for_status()
        except HTTPError as err:
            raise HttpTransportError(f"{str(err)} - {data}", response.status_code)

        return data

    async def _get_response_data(self, response: Response) -> dict[str, Any] | str:
        if "application/json" in response.headers.get("Content-Type") and len(response.content) > 0:
            return response.json()

        return response.text


async def init_httpx_transport() -> Generator[None, None, HttpxTransport]:
    client = AsyncClient()
    yield HttpxTransport(client=client)
    await client.aclose()
