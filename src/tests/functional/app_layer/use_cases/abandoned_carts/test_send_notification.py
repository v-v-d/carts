from http import HTTPMethod
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.app_layer.interfaces.clients.notifications.exceptions import (
    NotificationsClientError,
)
from app.app_layer.use_cases.abandoned_carts_service import AbandonedCartsService
from app.domain.cart_config.entities import CartConfig
from app.domain.carts.entities import Cart
from app.infra.http.transports.base import (
    HttpRequestInputDTO,
    HttpTransportConfig,
    HttpTransportError,
)
from tests.environment.unit_of_work import TestUow


@pytest.mark.parametrize("http_response", [{"returns": {}}], indirect=True)
async def test_ok(
    service: AbandonedCartsService,
    cart: Cart,
    cart_config: CartConfig,
    uow: TestUow,
    client_base_url: str,
    http_config: HttpTransportConfig,
    http_response: AsyncMock,
    http_session: MagicMock,
) -> None:
    await service.send_notification(user_id=cart.user_id, cart_id=cart.id)

    async with uow(autocommit=True):
        notification = await uow.carts_notifications.retrieve(cart_id=cart.id)

    assert notification is not None

    http_session.request.assert_called_once_with(
        method=HTTPMethod.POST,
        url=f"{client_base_url}notifications",
        headers={"Accept": "application/json"},
        params=None,
        data=None,
        json={"user_id": cart.user_id, "text": cart_config.abandoned_cart_text},
        trace_request_ctx=SimpleNamespace(
            data=HttpRequestInputDTO(
                method=HTTPMethod.POST,
                url=f"{client_base_url}notifications",
                headers={"Accept": "application/json"},
                params=None,
                body={"user_id": cart.user_id, "text": cart_config.abandoned_cart_text},
            ),
            integration_name=http_config.integration_name,
        ),
    )


@pytest.mark.parametrize(
    "http_response",
    [{"raises": HttpTransportError(message="test", code=0)}],
    indirect=True,
)
async def test_failed(
    service: AbandonedCartsService,
    cart: Cart,
    cart_config: CartConfig,
    uow: TestUow,
    client_base_url: str,
    http_config: HttpTransportConfig,
    http_response: AsyncMock,
    http_session: MagicMock,
) -> None:
    with pytest.raises(NotificationsClientError, match="test"):
        await service.send_notification(user_id=cart.user_id, cart_id=cart.id)

    async with uow(autocommit=True):
        notification = await uow.carts_notifications.retrieve(cart_id=cart.id)

    assert notification is None

    http_session.request.assert_called_once_with(
        method=HTTPMethod.POST,
        url=f"{client_base_url}notifications",
        headers={"Accept": "application/json"},
        params=None,
        data=None,
        json={"user_id": cart.user_id, "text": cart_config.abandoned_cart_text},
        trace_request_ctx=SimpleNamespace(
            data=HttpRequestInputDTO(
                method=HTTPMethod.POST,
                url=f"{client_base_url}notifications",
                headers={"Accept": "application/json"},
                params=None,
                body={"user_id": cart.user_id, "text": cart_config.abandoned_cart_text},
            ),
            integration_name=http_config.integration_name,
        ),
    )
