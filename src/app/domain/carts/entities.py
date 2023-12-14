from decimal import Decimal

from app.domain.carts.dto import CartDTO
from app.domain.items.entities import Item


class Cart:
    weight_item_qty: Decimal = Decimal(1)

    def __init__(self, data: CartDTO, items: list[Item]) -> None:
        self.id = data.id
        self.is_active = data.is_active
        self.items = items

    @property
    def items_qty(self) -> Decimal:
        return sum([self.weight_item_qty if item.is_weight else item.qty for item in self.items])

    @property
    def cost(self) -> Decimal:
        return sum([item.cost for item in self.items])

    def deactivate(self) -> None:
        self.is_active = False
