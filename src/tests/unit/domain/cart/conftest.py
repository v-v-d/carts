import pytest
from _pytest.fixtures import SubRequest

from app.domain.cart_config.dto import CartConfigDTO
from app.domain.cart_config.entities import CartConfig
from app.domain.cart_coupons.dto import CartCouponDTO
from app.domain.cart_coupons.entities import CartCoupon
from app.domain.cart_items.dto import ItemDTO
from app.domain.cart_items.entities import CartItem
from app.domain.carts.dto import CartDTO
from app.domain.carts.entities import Cart
from app.domain.carts.value_objects import CartStatusEnum
from tests.utils import fake


@pytest.fixture()
async def cart_config(request: SubRequest) -> CartConfig:
    extra_data = getattr(request, "param", {})

    return CartConfig(
        data=CartConfigDTO(
            **{
                "max_items_qty": fake.numeric.integer_number(start=1),
                "min_cost_for_checkout": fake.numeric.integer_number(start=1),
                "limit_items_by_id": {},
                "hours_since_update_until_abandoned": fake.numeric.integer_number(
                    start=1
                ),
                "max_abandoned_notifications_qty": fake.numeric.integer_number(start=1),
                "abandoned_cart_text": fake.text.word(),
                **extra_data,
            },
        ),
    )


@pytest.fixture()
async def cart(request: SubRequest, cart_config: CartConfig) -> Cart:
    extra_data = getattr(request, "param", {})

    return Cart(
        data=CartDTO(
            **{
                "created_at": fake.datetime.datetime(),
                "id": fake.cryptographic.uuid_object(),
                "user_id": fake.numeric.integer_number(start=1),
                "status": CartStatusEnum.OPENED,
                **extra_data,
            },
        ),
        items=[],
        config=cart_config,
    )


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
