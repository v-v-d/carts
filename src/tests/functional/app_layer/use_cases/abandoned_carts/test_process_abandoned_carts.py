from datetime import datetime, timedelta
from unittest.mock import AsyncMock, call

import pytest
from _pytest.fixtures import SubRequest

from app.api.events.tasks.abandoned_carts import send_abandoned_cart_notification
from app.app_layer.use_cases.abandoned_carts_service import AbandonedCartsService
from app.config import TaskConfig
from app.domain.cart_config.entities import CartConfig
from app.domain.cart_notifications.entities import CartNotification
from app.domain.carts.dto import CartDTO
from app.domain.carts.entities import Cart
from app.domain.carts.value_objects import CartStatusEnum
from app.infra.events.queues import QueueNameEnum
from tests.environment.unit_of_work import TestUow
from tests.utils import fake


@pytest.fixture()
async def carts_qty() -> int:
    return fake.numeric.integer_number(start=2, end=5)


@pytest.fixture()
async def user_ids(carts_qty: int) -> list[int]:
    return list(range(carts_qty))


@pytest.fixture()
async def carts(
    request: SubRequest,
    uow: TestUow,
    cart_config: CartConfig,
    user_ids: list[int],
) -> list[Cart]:
    extra_data = getattr(request, "param", {})
    last_update_at = datetime.now() - timedelta(
        hours=cart_config.hours_since_update_until_abandoned,
    )
    common_kwargs = {
        "created_at": last_update_at,
        "updated_at": last_update_at,
        **extra_data,
    }

    carts = [
        Cart(
            data=CartDTO(
                **{
                    "id": fake.cryptographic.uuid_object(),
                    "user_id": user_id,
                    "status": CartStatusEnum.OPENED,
                    **common_kwargs,
                },
            ),
            items=[],
            config=cart_config,
        )
        for user_id in user_ids
    ]

    async with uow(autocommit=True):
        await uow.carts.update_config(cart_config=cart_config)
        await uow.carts.bulk_create(carts=carts, **common_kwargs)

    return carts


@pytest.fixture()
async def notifications(
    carts: list[Cart],
    cart_config: CartConfig,
    uow: TestUow,
) -> list[CartNotification]:
    notifications = [
        CartNotification.create_abandoned_cart_notification(
            cart_id=cart.id,
            text=cart_config.abandoned_cart_text,
        )
        for cart in carts
        for _ in range(cart_config.max_abandoned_notifications_qty)
    ]

    async with uow(autocommit=True):
        await uow.carts_notifications.bulk_create(notifications=notifications)

    return notifications


async def test_ok(
    service: AbandonedCartsService, broker: AsyncMock, carts: list[Cart]
) -> None:
    await service.process_abandoned_carts()

    expected_calls = [
        call(
            function=send_abandoned_cart_notification.__name__,
            user_id=cart.user_id,
            cart_id=cart.id,
            _job_id=str(cart.id),
            _queue_name=QueueNameEnum.EXAMPLE_QUEUE.value,
        )
        for cart in carts
    ]
    broker.enqueue_job.assert_has_awaits(calls=expected_calls)


@pytest.mark.parametrize("carts", [{"updated_at": datetime.now()}], indirect=True)
async def test_no_abandoned_carts(
    service: AbandonedCartsService, carts: list[Cart], broker: AsyncMock
) -> None:
    await service.process_abandoned_carts()
    broker.enqueue_job.assert_not_awaited()


@pytest.mark.parametrize(
    "cart_config", [{"max_abandoned_notifications_qty": 2}], indirect=True
)
@pytest.mark.usefixtures("carts", "notifications")
async def test_already_processed(
    service: AbandonedCartsService,
    cart_config: CartConfig,
    broker: AsyncMock,
) -> None:
    await service.process_abandoned_carts()
    broker.enqueue_job.assert_not_awaited()


async def test_config_ok(service: AbandonedCartsService) -> None:
    assert isinstance(service.config, TaskConfig)
    assert service.config == service._config
