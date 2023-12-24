from decimal import Decimal

import pytest

from app.domain.cart_items.dto import ItemDTO
from app.domain.cart_items.entities import CartItem
from app.domain.cart_items.exceptions import MinQtyLimitExceededError
from tests.utils import fake


async def test_calculate_cost() -> None:
    item = CartItem(
        data=ItemDTO(
            id=fake.numeric.integer_number(start=1),
            name=fake.text.word(),
            qty=Decimal(2),
            price=Decimal(3),
        )
    )
    assert item.cost == Decimal(6)


async def test_qty_validation_ok() -> None:
    item = CartItem(
        data=ItemDTO(
            id=fake.numeric.integer_number(start=1),
            name=fake.text.word(),
            qty=Decimal(CartItem.MIN_VALID_QTY),
            price=fake.numeric.integer_number(start=1, end=99),
        )
    )
    item.check_item_qty_above_min()


async def test_qty_validation_failed() -> None:
    item = CartItem(
        data=ItemDTO(
            id=fake.numeric.integer_number(start=1),
            name=fake.text.word(),
            qty=Decimal(CartItem.MIN_VALID_QTY - 1),
            price=fake.numeric.integer_number(start=1, end=99),
        )
    )

    with pytest.raises(MinQtyLimitExceededError):
        item.check_item_qty_above_min()
