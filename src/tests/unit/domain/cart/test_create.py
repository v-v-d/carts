from datetime import datetime
from decimal import Decimal
from uuid import UUID

import pytest

from app.domain.cart_config.entities import CartConfig
from app.domain.carts.entities import Cart
from app.domain.carts.value_objects import CartStatusEnum

FROZEN_TIME = datetime.now()

pytestmark = [pytest.mark.freeze_time(FROZEN_TIME)]


def test_ok(cart_config: CartConfig) -> None:
    cart = Cart.create(user_id=1, config=cart_config)

    assert cart.created_at == FROZEN_TIME
    assert isinstance(cart.id, UUID)
    assert cart.user_id == 1
    assert cart.status == CartStatusEnum.OPENED
    assert cart.items == []
    assert cart.coupon is None
    assert cart.items_qty == Decimal(0)
    assert cart.cost == Decimal(0)
    assert cart.checkout_enabled == (cart.cost >= cart_config.min_cost_for_checkout)
