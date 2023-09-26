from typing import Any, Mapping, Generator

from httpx import AsyncClient, HTTPError

from infra.http.transports.base import IHttpTransport, BaseHttpTransportError


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
        async with self._client.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data if isinstance(data, str) else None,
            json=data if isinstance(data, (dict, list)) else None,
        ) as response:
            try:
                response.raise_for_status()
            except HTTPError as err:
                raise BaseHttpTransportError(response.status_code, str(err))

            return response


async def init_httpx_transport() -> Generator[None, None, HttpxTransport]:
    client = AsyncClient()
    yield HttpxTransport(client=client)
    await client.aclose()
