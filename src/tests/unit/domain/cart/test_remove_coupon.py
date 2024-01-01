import pytest

from app.domain.cart_coupons.entities import CartCoupon
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import CouponDoesNotExistError, OperationForbiddenError
from app.domain.carts.value_objects import CartStatusEnum


def test_ok(cart: Cart, coupon: CartCoupon) -> None:
    cart.set_coupon(coupon=coupon)
    cart.remove_coupon()

    assert cart.coupon is None


@pytest.mark.parametrize(
    "cart",
    [
        pytest.param({"status": status}, id=status)
        for status in CartStatusEnum
        if status != CartStatusEnum.OPENED
    ],
    indirect=True,
)
def test_cart_cant_be_modified(cart: Cart, coupon: CartCoupon) -> None:
    cart.set_coupon(coupon=coupon)

    with pytest.raises(OperationForbiddenError, match=""):
        cart.remove_coupon()


def test_failed(cart: Cart) -> None:
    with pytest.raises(CouponDoesNotExistError, match=""):
        cart.remove_coupon()
