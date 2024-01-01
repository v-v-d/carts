import pytest

from app.domain.cart_config.entities import CartConfig
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import ChangeStatusError
from app.domain.carts.value_objects import CartStatusEnum


@pytest.mark.parametrize("cart_config", [{"min_cost_for_checkout": 0}], indirect=True)
def test_ok(cart: Cart, cart_config: CartConfig) -> None:
    cart.lock()
    cart.unlock()
    assert cart.status == CartStatusEnum.OPENED


@pytest.mark.parametrize(
    "cart",
    [
        pytest.param({"status": status}, id=status)
        for status in CartStatusEnum
        if CartStatusEnum.OPENED not in Cart.STATUS_TRANSITION_RULESET[status]
    ],
    indirect=True,
)
def test_invalid_cart_status(cart: Cart) -> None:
    with pytest.raises(ChangeStatusError, match=""):
        cart.unlock()
