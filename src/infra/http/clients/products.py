from http import HTTPMethod
from typing import Any, Type

from furl import furl
from pydantic import AnyHttpUrl, ValidationError, BaseModel

from app.interfaces.clients.products.dto import ProductOutputDTO
from app.interfaces.clients.products.exceptions import ProductsClientError
from app.interfaces.clients.products.client import IProductsClient
from infra.http.transports.base import IHttpTransport, HttpTransportError


class ProductsHttpClient(IProductsClient):
    def __init__(self, base_url: AnyHttpUrl, transport: IHttpTransport) -> None:
        self._base_url = base_url
        self._transport = transport

    async def get_product(self, item_id: int) -> ProductOutputDTO:
        url = furl(self._base_url).add(path="products").add(path=str(item_id)).url
        response = await self._try_to_make_request(HTTPMethod.GET, url)

        return self._try_to_get_dto(ProductOutputDTO, response)

    async def _try_to_make_request(self, *args, **kwargs) -> Any:
        try:
            return await self._transport.request(*args, **kwargs)
        except HttpTransportError as err:
            raise ProductsClientError(f"{err.code} - {err.message}")

    def _try_to_get_dto(self, dto_model: Type[BaseModel], response: dict[str, Any] | str) -> Any:
        try:
            return dto_model(**response)
        except (ValidationError, TypeError) as err:
            raise ProductsClientError(f"{str(err)} - {response}")
