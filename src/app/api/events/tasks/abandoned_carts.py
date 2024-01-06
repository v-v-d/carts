from typing import Any
from uuid import UUID

from arq import Retry
from dependency_injector.wiring import Provide, inject

from app.app_layer.interfaces.clients.notifications.exceptions import (
    NotificationsClientError,
)
from app.app_layer.use_cases.abandoned_carts_service import AbandonedCartsService
from app.containers import Container


@inject
async def send_abandoned_cart_notification(
    ctx: [str, Any],
    user_id: int,
    cart_id: UUID,
    service: AbandonedCartsService = Provide[Container.abandoned_carts_service],
) -> None:
    try:
        await service.send_notification(user_id=user_id, cart_id=cart_id)
    except NotificationsClientError:
        raise Retry(defer=service.config.retry_delay_sec * ctx["job_try"])


@inject
async def process_abandoned_carts(
    _ctx: [str, Any],
    service: AbandonedCartsService = Provide[Container.abandoned_carts_service],
) -> None:
    await service.process_abandoned_carts()
