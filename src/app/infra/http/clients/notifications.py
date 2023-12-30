from http import HTTPMethod
from typing import Any

from furl import furl
from pydantic import AnyHttpUrl

from app.app_layer.interfaces.clients.notifications.client import INotificationClient
from app.app_layer.interfaces.clients.notifications.dto import SendNotificationInputDTO
from app.app_layer.interfaces.clients.notifications.exceptions import (
    NotificationsClientError,
)
from app.infra.http.transports.base import (
    HttpRequestInputDTO,
    HttpTransportError,
    IHttpTransport,
)


class NotificationsHttpClient(INotificationClient):
    def __init__(self, base_url: AnyHttpUrl, transport: IHttpTransport) -> None:
        self._base_url = base_url
        self._transport = transport

    async def send_notification(self, data: SendNotificationInputDTO) -> None:
        url = furl(self._base_url).add(path="notifications").url

        await self._try_to_make_request(
            data=HttpRequestInputDTO(
                method=HTTPMethod.POST,
                url=url,
                headers={"Accept": "application/json"},
                body={
                    "user_id": data.user_id,
                    "text": data.text,
                },
            ),
        )

    async def _try_to_make_request(self, *args, **kwargs) -> Any:
        try:
            return await self._transport.request(*args, **kwargs)
        except HttpTransportError as err:
            raise NotificationsClientError(str(err))
