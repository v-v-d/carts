from contextlib import contextmanager
from decimal import Decimal
from typing import ContextManager

from app.domain.carts.dto import CartDTO
from app.domain.carts.exceptions import ItemDoesNotExistInCartError
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

    def increase_item_qty(self, item_id: int, qty: Decimal) -> None:
        with self._change_items() as items_by_id:
            items_by_id[item_id].qty += qty

    def add_new_item(self, item: Item) -> None:
        self.items.append(item)

    def deactivate(self) -> None:
        self.is_active = False

    def get_item(self, item_id: int) -> Item:
        items_by_id = {item.id: item for item in self.items}

        if item_id not in items_by_id:
            raise ItemDoesNotExistInCartError

        return items_by_id[item_id]

    def decrease_item_qty(self, item_id: int, qty: Decimal) -> None:
        with self._change_items() as items_by_id:
            items_by_id[item_id].qty -= qty

    def remove_item(self, item: Item) -> None:
        with self._change_items() as items_by_id:
            items_by_id.pop(item.id)

    @contextmanager
    def _change_items(self) -> ContextManager[dict[int: Item]]:
        items_by_id = {item.id: item for item in self.items}
        yield items_by_id
        self.items = list(items_by_id.values())
