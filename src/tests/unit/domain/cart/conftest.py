import pytest
from _pytest.fixtures import SubRequest

from app.domain.cart_config.entities import CartConfig
from app.domain.cart_coupons.dto import CartCouponDTO
from app.domain.cart_coupons.entities import CartCoupon
from app.domain.cart_items.dto import ItemDTO
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from tests.utils import fake


@pytest.fixture()
async def cart_item(request: SubRequest, cart: Cart, cart_config: CartConfig) -> CartItem:
    extra_data = getattr(request, "param", {})

    return CartItem(
        data=ItemDTO(
            **{
                "id": fake.numeric.integer_number(start=1),
                "name": fake.text.word(),
                "qty": fake.numeric.integer_number(
                    start=1,
                    end=cart_config.max_items_qty,
                ),
                "price": fake.numeric.decimal_number(start=1),
                "is_weight": fake.choice.choice([True, False]),
                "cart_id": cart.id,
                **extra_data,
            },
        ),
    )


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
