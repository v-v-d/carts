import pytest

from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import ChangeStatusError
from app.domain.carts.value_objects import CartStatusEnum


def test_ok(cart: Cart) -> None:
    cart.deactivate()
    assert cart.status == CartStatusEnum.DEACTIVATED


@pytest.mark.parametrize(
    "cart",
    [
        pytest.param({"status": status}, id=status)
        for status in CartStatusEnum
        if status != CartStatusEnum.OPENED
    ],
    indirect=True,
)
def test_cart_has_invalid_status(cart: Cart) -> None:
    with pytest.raises(ChangeStatusError, match=""):
        cart.deactivate()
