from typing import Any, Mapping, Generator

from aiohttp import ClientSession, ClientResponseError, ClientResponse

from infra.http.transports.base import IHttpTransport, BaseHttpTransportError


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
                raise BaseHttpTransportError(err.status, data)

            return data

    async def _get_response_data(self, response: ClientResponse) -> dict[str, Any] | str:
        if response.content_type == "application/json":
            return await response.json()

        return await response.text()


async def init_aiohttp_transport() -> Generator[None, None, AioHttpTransport]:
    session = ClientSession()
    transport = AioHttpTransport(session=session)
    yield transport
    await session.close()
