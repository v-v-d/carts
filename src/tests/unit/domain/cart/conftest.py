import pytest
from _pytest.fixtures import SubRequest

from app.domain.cart_coupons.dto import CartCouponDTO
from app.domain.cart_coupons.entities import CartCoupon
from app.domain.carts.entities import Cart
from tests.utils import fake


@pytest.fixture()
async def coupon(request: SubRequest, cart: Cart) -> CartCoupon:
    extra_data = getattr(request, "param", {})

    return CartCoupon(
        cart=cart,
        data=CartCouponDTO(
            **{
                "coupon_id": fake.text.word(),
                "min_cart_cost": fake.numeric.decimal_number(start=1),
                "discount_abs": fake.numeric.decimal_number(start=1),
                **extra_data,
            },
        ),
    )
