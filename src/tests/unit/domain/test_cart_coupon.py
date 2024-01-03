import pytest

from app.domain.cart_coupons.dto import CartCouponDTO
from app.domain.cart_coupons.entities import CartCoupon
from app.domain.cart_coupons.exceptions import (
    CartCostValidationError,
    DiscountValidationError,
)
from app.domain.carts.entities import Cart
from tests.utils import fake


def test_init_ok(cart: Cart) -> None:
    coupon = CartCoupon(
        data=CartCouponDTO(
            coupon_id=fake.text.word(),
            min_cart_cost=fake.numeric.integer_number(start=1),
            discount_abs=fake.numeric.integer_number(start=1),
        ),
        cart=cart,
    )

    assert coupon.cart_cost == cart.cost - coupon.discount_abs
    assert coupon.applied is (cart.cost >= coupon.min_cart_cost)


def test_min_cart_cost_invalid() -> None:
    with pytest.raises(CartCostValidationError, match=""):
        CartCouponDTO(
            coupon_id=fake.text.word(),
            min_cart_cost=fake.numeric.integer_number(start=-100, end=-1),
            discount_abs=fake.numeric.integer_number(start=1),
        )


def test_discount_abs_invalid() -> None:
    with pytest.raises(DiscountValidationError, match=""):
        CartCouponDTO(
            coupon_id=fake.text.word(),
            min_cart_cost=fake.numeric.integer_number(start=0),
            discount_abs=fake.numeric.integer_number(start=-100, end=0),
        )
