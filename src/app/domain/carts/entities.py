from decimal import Decimal
from uuid import UUID

from app.domain.items.entities import Item


class Cart:
    weight_item_qty: Decimal = Decimal(1)

    def __init__(self, cart_id: UUID, items: list[Item]) -> None:
        self.id = cart_id
        self.items = items

    @property
    def items_qty(self) -> Decimal:
        return sum([self.weight_item_qty if item.is_weight else item.qty for item in self.items])

    @property
    def cost(self) -> Decimal:
        return sum([item.cost for item in self.items])
