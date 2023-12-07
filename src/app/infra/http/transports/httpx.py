import asyncio
from typing import Any, Generator

from httpx import AsyncClient, HTTPError, Response

from app.infra.http.transports.base import HttpRequestInputDTO, HttpTransportError, IHttpTransport


class HttpxTransport(IHttpTransport):
    min_response_content_len: int = 0

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def request(self, data: HttpRequestInputDTO) -> dict[str, Any] | str:
        try:
            return await self._try_to_make_request(data)
        except (asyncio.TimeoutError, BrokenPipeError) as err:
            raise HttpTransportError(str(err))

    async def _try_to_make_request(self, data: HttpRequestInputDTO) -> dict[str, Any] | str:
        response = await self._client.request(
            method=data.method,
            url=data.url,
            headers=data.headers,
            params=data.params,
            data=data.body if isinstance(data.body, str) else None,
            json=data.body if isinstance(data.body, (dict, list)) else None,
        )

        parsed_data = self._get_response_data(response)

        try:
            response.raise_for_status()
        except HTTPError as err:
            raise HttpTransportError(f"{str(err)} - {parsed_data}", response.status_code)

        return parsed_data

    def _get_response_data(self, response: Response) -> dict[str, Any] | str:
        if (
            "application/json" in response.headers.get("Content-Type")
            and len(response.content) > self.min_response_content_len
        ):
            return response.json()

        return response.text


async def init_httpx_transport() -> Generator[None, None, HttpxTransport]:
    client = AsyncClient()
    yield HttpxTransport(client=client)
    await client.aclose()
