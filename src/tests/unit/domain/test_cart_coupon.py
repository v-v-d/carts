from app.domain.cart_coupons.dto import CartCouponDTO
from app.domain.cart_coupons.entities import CartCoupon
from app.domain.carts.entities import Cart
from tests.utils import fake


def test_ok(cart: Cart) -> None:
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
