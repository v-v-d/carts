import pytest

from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import CartItemDoesNotExistError, OperationForbiddenError
from app.domain.carts.value_objects import CartStatusEnum


def test_ok(cart: Cart, cart_item: CartItem) -> None:
    cart.add_new_item(item=cart_item)
    cart.delete_item(item_id=cart_item.id)

    assert len(cart.items) == 0


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
        cart.delete_item(item_id=cart_item.id)


def test_item_doesnt_exist(cart: Cart, cart_item: CartItem) -> None:
    with pytest.raises(CartItemDoesNotExistError, match=""):
        cart.delete_item(item_id=cart_item.id)
