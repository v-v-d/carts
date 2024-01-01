import pytest

from app.domain.cart_items.dto import ItemDTO
from app.domain.cart_items.entities import CartItem
from app.domain.cart_items.exceptions import MinQtyLimitExceededError
from tests.utils import fake


def test_init_ok() -> None:
    item = CartItem(
        data=ItemDTO(
            id=fake.numeric.integer_number(start=1),
            name=fake.text.word(),
            qty=fake.numeric.integer_number(start=1),
            price=fake.numeric.integer_number(start=1),
            is_weight=fake.random.choice([True, False]),
            cart_id=fake.cryptographic.uuid_object(),
        )
    )

    assert item.cost == item.price * item.qty


def test_qty_invalid() -> None:
    with pytest.raises(MinQtyLimitExceededError, match=""):
        ItemDTO(
            id=fake.numeric.integer_number(start=1),
            name=fake.text.word(),
            qty=fake.numeric.integer_number(start=-100, end=0),
            price=fake.numeric.integer_number(start=1),
            is_weight=fake.random.choice([True, False]),
            cart_id=fake.cryptographic.uuid_object(),
        )
