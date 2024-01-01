import pytest

from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import OperationForbiddenError
from app.domain.carts.value_objects import CartStatusEnum


def test_ok(cart: Cart, cart_item: CartItem) -> None:
    cart.add_new_item(item=cart_item)
    cart.clear()

    assert cart.items == []


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
        cart.clear()
