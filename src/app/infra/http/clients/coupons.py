from http import HTTPMethod
from typing import Any, Type

from furl import furl
from pydantic import AnyHttpUrl, BaseModel, ValidationError

from app.app_layer.interfaces.clients.coupons.client import ICouponsClient
from app.app_layer.interfaces.clients.coupons.dto import CouponOutputDTO
from app.app_layer.interfaces.clients.coupons.exceptions import CouponsClientError
from app.infra.http.transports.base import (
    HttpRequestInputDTO,
    HttpTransportError,
    IHttpTransport,
)


class CouponsHttpClient(ICouponsClient):
    """
    Responsible for making HTTP requests to retrieve coupon information from a
    remote server.
    """

    def __init__(self, base_url: AnyHttpUrl, transport: IHttpTransport) -> None:
        self._base_url = base_url
        self._transport = transport

    async def get_coupon(self, coupon_name: str) -> CouponOutputDTO:
        """
        Retrieves a coupon by name from the remote server. It constructs the URL,
        makes the HTTP request, and returns the parsed CouponOutputDTO object.
        """

        url = furl(self._base_url).add(path="coupons").url

        response = await self._try_to_make_request(
            data=HttpRequestInputDTO(
                method=HTTPMethod.GET,
                url=url,
                headers={"Accept": "application/json"},
                params={"name": coupon_name},
            ),
        )

        return self._try_to_get_dto(CouponOutputDTO, response)

    async def _try_to_make_request(self, *args, **kwargs) -> Any:
        try:
            return await self._transport.request(*args, **kwargs)
        except HttpTransportError as err:
            raise CouponsClientError(str(err))

    def _try_to_get_dto(
        self, dto_model: Type[BaseModel], response: dict[str, Any] | str
    ) -> Any:
        try:
            return dto_model.model_validate(response)
        except (ValidationError, TypeError) as err:
            raise CouponsClientError(f"{str(err)} - {response}")
