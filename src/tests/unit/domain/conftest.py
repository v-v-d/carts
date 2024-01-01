import pytest
from _pytest.fixtures import SubRequest

from app.domain.cart_config.dto import CartConfigDTO
from app.domain.cart_config.entities import CartConfig
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
