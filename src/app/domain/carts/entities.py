import uuid
from contextlib import contextmanager
from decimal import Decimal
from logging import getLogger
from typing import ContextManager

from app.domain.carts.dto import CartDTO
from app.domain.carts.exceptions import CartItemDoesNotExistError
from app.domain.items.entities import Item

logger = getLogger(__name__)


class Cart:
    weight_item_qty: Decimal = Decimal(1)

    def __init__(self, data: CartDTO, items: list[Item]) -> None:
        self.id = data.id
        self.user_id = data.user_id
        self.is_active = data.is_active
        self.items = items

    @property
    def items_qty(self) -> Decimal:
        return sum([self.weight_item_qty if item.is_weight else item.qty for item in self.items])

    @property
    def cost(self) -> Decimal:
        return sum([item.cost for item in self.items])

    @classmethod
    def create(cls, user_id: int) -> "Cart":
        return cls(
            data=CartDTO(
                id=uuid.uuid4(),
                user_id=user_id,
                is_active=True,
            ),
            items=[],
        )

    def increase_item_qty(self, item_id: int, qty: Decimal) -> None:
        with self._change_items() as items_by_id:
            old_qty = items_by_id[item_id].qty
            items_by_id[item_id].qty += qty
            logger.debug(
                "Cart %s, item %s. Item qty changed from %s to %s.",
                self.id,
                item_id,
                old_qty,
                items_by_id[item_id].qty,
            )

    def add_new_item(self, item: Item) -> None:
        self.items.append(item)
        logger.debug(
            "Cart %s. New item %s with %s qty added to cart.",
            self.id,
            item.id,
            item.qty,
        )

    def deactivate(self) -> None:
        self.is_active = False
        logger.debug("Cart %s deactivated.", self.id)

    def get_item(self, item_id: int) -> Item:
        items_by_id = {item.id: item for item in self.items}

        if item_id not in items_by_id:
            logger.debug("Cart %s, item %s doesn't exist in cart.", self.id, item_id)
            raise CartItemDoesNotExistError

        return items_by_id[item_id]

    def update_item_qty(self, item_id: int, qty: Decimal) -> None:
        with self._change_items() as items_by_id:
            old_qty = items_by_id[item_id].qty
            items_by_id[item_id].qty = qty
            logger.debug(
                "Cart %s, item %s. Item qty changed from %s to %s.",
                self.id,
                item_id,
                old_qty,
                items_by_id[item_id].qty,
            )

    def delete_item(self, item: Item) -> None:
        with self._change_items() as items_by_id:
            items_by_id.pop(item.id)
            logger.debug("Cart %s, item %s deleted.", self.id, item.id)

    def clear(self) -> None:
        self.items = []
        logger.debug("Cart %s has been cleared.", self.id)

    @contextmanager
    def _change_items(self) -> ContextManager[dict[int:Item]]:
        items_by_id = {item.id: item for item in self.items}
        yield items_by_id
        self.items = list(items_by_id.values())
