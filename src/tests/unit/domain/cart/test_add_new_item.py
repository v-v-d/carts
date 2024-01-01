from decimal import Decimal

import pytest

from app.domain.cart_config.entities import CartConfig
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import (
    CartItemAlreadyExistsError,
    MaxItemsQtyLimitExceeded,
    OperationForbiddenError,
    SpecificItemQtyLimitExceeded,
)
from app.domain.carts.value_objects import CartStatusEnum


def test_ok(cart: Cart, cart_item: CartItem) -> None:
    cart.add_new_item(item=cart_item)
    assert len(cart.items) == 1


@pytest.mark.parametrize(
    "cart",
    [
        pytest.param({"status": status}, id=status)
        for status in CartStatusEnum
        if status != CartStatusEnum.OPENED
    ],
    indirect=True,
)
def test_cart_cant_be_modified(cart: Cart, cart_item: CartItem) -> None:
    with pytest.raises(OperationForbiddenError, match=""):
        cart.add_new_item(item=cart_item)


def test_item_already_exists(
    cart: Cart, cart_config: CartConfig, cart_item: CartItem
) -> None:
    cart.add_new_item(item=cart_item)

    with pytest.raises(CartItemAlreadyExistsError, match=""):
        cart.add_new_item(item=cart_item)


@pytest.mark.parametrize(
    ("cart_config", "cart_item"),
    [({"limit_items_by_id": {1: Decimal(0)}}, {"id": 1, "qty": Decimal(1)})],
    indirect=True,
)
def test_item_qty_limit_exceeded(
    cart: Cart,
    cart_config: CartConfig,
    cart_item: CartItem,
) -> None:
    with pytest.raises(SpecificItemQtyLimitExceeded, match="limit: 0, actual: 1"):
        cart.add_new_item(item=cart_item)


@pytest.mark.parametrize(
    ("cart_config", "cart_item"),
    [({"max_items_qty": Decimal(1)}, {"id": 1, "qty": Decimal(2), "is_weight": False})],
    indirect=True,
)
def test_cart_items_qty_limit_exceeded(
    cart: Cart,
    cart_config: CartConfig,
    cart_item: CartItem,
) -> None:
    with pytest.raises(MaxItemsQtyLimitExceeded, match=""):
        cart.add_new_item(item=cart_item)
