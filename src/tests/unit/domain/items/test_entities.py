from decimal import Decimal

import pytest

from app.domain.items.dto import ItemDTO
from app.domain.items.entities import Item
from app.domain.items.exceptions import QtyValidationError
from tests.utils import fake


async def test_calculate_cost() -> None:
    item = Item(
        data=ItemDTO(
            id=fake.numeric.integer_number(start=1),
            name=fake.text.word(),
            qty=Decimal(2),
            price=Decimal(3),
        )
    )
    assert item.cost == Decimal(6)


async def test_qty_validation_ok() -> None:
    item = Item(
        data=ItemDTO(
            id=fake.numeric.integer_number(start=1),
            name=fake.text.word(),
            qty=Decimal(Item.min_valid_qty),
            price=fake.numeric.integer_number(start=1, end=99),
        )
    )
    item.validate_qty()


async def test_qty_validation_failed() -> None:
    item = Item(
        data=ItemDTO(
            id=fake.numeric.integer_number(start=1),
            name=fake.text.word(),
            qty=Decimal(Item.min_valid_qty - 1),
            price=fake.numeric.integer_number(start=1, end=99),
        )
    )

    with pytest.raises(QtyValidationError):
        item.validate_qty()
