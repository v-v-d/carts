import pytest

from app.domain.cart_coupons.entities import CartCoupon
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import CouponAlreadyAppliedError


def test_ok(cart: Cart) -> None:
    cart.check_can_coupon_be_applied()


def test_failed(cart: Cart, coupon: CartCoupon) -> None:
    cart.set_coupon(coupon=coupon)

    with pytest.raises(CouponAlreadyAppliedError, match=""):
        cart.check_can_coupon_be_applied()
