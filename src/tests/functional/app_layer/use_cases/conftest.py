import pytest

from app.domain.cart_config.entities import CartConfig
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from tests.environment.unit_of_work import TestUow


@pytest.fixture()
async def cart(
    uow: TestUow,
    cart: Cart,
    cart_item: CartItem,
    cart_config: CartConfig,
) -> Cart:
    cart.add_new_item(item=cart_item)

    async with uow(autocommit=True):
        await uow.carts.update_config(cart_config=cart_config)
        await uow.carts.create(cart=cart)
        await uow.items.add_item(item=cart_item)

    return cart


@pytest.fixture()
def auth_data() -> str:
    return "Bearer customer.1"
