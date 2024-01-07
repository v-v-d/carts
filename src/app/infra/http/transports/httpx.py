import asyncio
from typing import Any, Generator

from httpx import AsyncClient, HTTPError, Response

from app.infra.http.transports.base import (
    HttpRequestInputDTO,
    HttpTransportError,
    IHttpTransport,
)


class HttpxTransport(IHttpTransport):
    """
    Provides a method called request which sends an HTTP request using the httpx
    library and returns the response data.
    """

    min_response_content_len: int = 0

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def request(self, data: HttpRequestInputDTO) -> dict[str, Any] | str:
        """
        Sends an HTTP request using the provided request data and returns the
        response data. If the response is successful, it returns a dictionary. If
        there is an error, it returns a string with the error message.
        """

        try:
            return await self._try_to_make_request(data)
        except (asyncio.TimeoutError, BrokenPipeError) as err:
            raise HttpTransportError(str(err))

    async def _try_to_make_request(
        self, data: HttpRequestInputDTO
    ) -> dict[str, Any] | str:
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


async def init_httpx_client() -> Generator[None, None, AsyncClient]:
    """
    Returns an asynchronous generator. The generator creates an instance of the
    AsyncClient class from the httpx library, yields it, and then closes it when
    the generator is finished.
    """

    client = AsyncClient()
    yield client
    await client.aclose()
