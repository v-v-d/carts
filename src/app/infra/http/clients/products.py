from http import HTTPMethod
from typing import Any, Type

from furl import furl
from pydantic import AnyHttpUrl, BaseModel, ValidationError

from app.app_layer.interfaces.clients.products.client import IProductsClient
from app.app_layer.interfaces.clients.products.dto import ProductOutputDTO
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.infra.http.transports.base import (
    HttpRequestInputDTO,
    HttpTransportError,
    IHttpTransport,
)


class ProductsHttpClient(IProductsClient):
    """
    Responsible for making HTTP requests to retrieve product information from a
    remote server.
    """

    def __init__(self, base_url: AnyHttpUrl, transport: IHttpTransport) -> None:
        self._base_url = base_url
        self._transport = transport

    async def get_product(self, item_id: int) -> ProductOutputDTO:
        """
        Retrieves product information by item ID. It constructs the request URL,
        makes the HTTP GET request, and returns the product information as a
        ProductOutputDTO object.
        """

        url = furl(self._base_url).add(path="products").add(path=str(item_id)).url
        response = await self._try_to_make_request(
            data=HttpRequestInputDTO(
                method=HTTPMethod.GET,
                url=url,
            ),
        )

        return self._try_to_get_dto(ProductOutputDTO, response)

    async def _try_to_make_request(self, *args, **kwargs) -> Any:
        try:
            return await self._transport.request(*args, **kwargs)
        except HttpTransportError as err:
            raise ProductsClientError(str(err))

    def _try_to_get_dto(
        self, dto_model: Type[BaseModel], response: dict[str, Any] | str
    ) -> Any:
        try:
            return dto_model.model_validate(response)
        except (ValidationError, TypeError) as err:
            raise ProductsClientError(f"{str(err)} - {response}")
