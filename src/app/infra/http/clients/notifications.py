from http import HTTPMethod
from logging import getLogger
from typing import Any

from furl import furl
from pydantic import AnyHttpUrl

from app.app_layer.interfaces.clients.notifications.client import INotificationsClient
from app.app_layer.interfaces.clients.notifications.dto import SendNotificationInputDTO
from app.app_layer.interfaces.clients.notifications.exceptions import (
    NotificationsClientError,
)
from app.infra.http.transports.base import (
    HttpRequestInputDTO,
    HttpTransportError,
    IHttpTransport,
)

logger = getLogger(__name__)


class NotificationsHttpClient(INotificationsClient):
    """
    Responsible for sending notifications to a specified user using an HTTP transport.
    It implements the INotificationsClient interface and uses an IHttpTransport
    instance to make the HTTP request.
    """

    def __init__(self, base_url: AnyHttpUrl, transport: IHttpTransport) -> None:
        self._base_url = base_url
        self._transport = transport

    async def send_notification(self, data: SendNotificationInputDTO) -> None:
        """
        Sends a notification to the user by making an HTTP POST request. It constructs
        the request URL by appending "/notifications" to the base URL. The request
        body includes the user ID and text from the SendNotificationInputDTO. It makes
        the request and handles any HttpTransportError that occurs.
        """

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
            logger.error("Failed to send abandoned cart notification! Error: %s", err)
            raise NotificationsClientError(str(err))
