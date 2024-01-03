from datetime import datetime
from uuid import UUID

import pytest

from app.domain.cart_notifications.entities import CartNotification
from app.domain.cart_notifications.value_objects import CartNotificationTypeEnum
from tests.utils import fake

FROZEN_TIME = datetime.now()

pytestmark = [pytest.mark.freeze_time(FROZEN_TIME)]


def test_create_ok() -> None:
    notification = CartNotification.create(
        cart_id=fake.cryptographic.uuid_object(),
        notification_type=CartNotificationTypeEnum.ABANDONED_CART,
        text=fake.text.word(),
    )

    assert isinstance(notification.id, UUID)
    assert notification.sent_at == FROZEN_TIME


def test_create_abandoned_cart_notification_ok() -> None:
    notification = CartNotification.create_abandoned_cart_notification(
        cart_id=fake.cryptographic.uuid_object(),
        text=fake.text.word(),
    )

    assert isinstance(notification.id, UUID)
    assert notification.type == CartNotificationTypeEnum.ABANDONED_CART
    assert notification.sent_at == FROZEN_TIME
