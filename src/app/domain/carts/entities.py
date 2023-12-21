import uuid
from contextlib import contextmanager
from decimal import Decimal
from logging import getLogger
from typing import ContextManager

from app.config import CartConfig
from app.domain.cart_items.entities import CartItem
from app.domain.carts.dto import CartDTO
from app.domain.carts.exceptions import (
    CartItemDoesNotExistError,
    NotOwnedByUserError,
    MaxItemsQtyLimitExceeded,
)
from app.domain.carts.value_objects import CartStatusEnum

logger = getLogger(__name__)


class Cart:
    def __init__(self, data: CartDTO, items: list[CartItem], config: CartConfig) -> None:
        self.id = data.id
        self.user_id = data.user_id
        self.status = data.status
        self.items = items

        self._config = config

    @property
    def items_qty(self) -> Decimal:
        return sum([self._config.weight_item_qty if item.is_weight else item.qty for item in self.items])

    @property
    def cost(self) -> Decimal:
        return sum([item.cost for item in self.items])

    @classmethod
    def create(cls, user_id: int, config: CartConfig) -> "Cart":
        return cls(
            data=CartDTO(
                id=uuid.uuid4(),
                user_id=user_id,
                status=CartStatusEnum.OPENED,
            ),
            items=[],
            config=config,
        )

    def increase_item_qty(self, item_id: int, qty: Decimal) -> None:
        with self._change_items() as items_by_id:
            item = items_by_id[item_id]
            self._validate_items_qty_limit()

            old_qty = items_by_id[item_id].qty
            items_by_id[item_id].qty += qty
            logger.debug(
                "Cart %s, item %s. Item qty changed from %s to %s.",
                self.id,
                item_id,
                old_qty,
                items_by_id[item_id].qty,
            )

    def add_new_item(self, item: CartItem) -> None:
        self.items.append(item)
        logger.debug(
            "Cart %s. New item %s with %s qty added to cart.",
            self.id,
            item.id,
            item.qty,
        )

    def deactivate(self) -> None:
        self.status = CartStatusEnum.DEACTIVATED
        logger.debug("Cart %s deactivated.", self.id)

    def get_item(self, item_id: int) -> CartItem:
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

    def delete_item(self, item: CartItem) -> None:
        with self._change_items() as items_by_id:
            items_by_id.pop(item.id)
            logger.debug("Cart %s, item %s deleted.", self.id, item.id)

    def clear(self) -> None:
        self.items = []
        logger.debug("Cart %s has been cleared.", self.id)

    def check_user_ownership(self, user_id: int) -> None:
        if self.user_id != user_id:
            logger.debug(
                "Cart %s. Invalid user_id detected! Expected %s, got %s",
                self.id,
                self.user_id,
                user_id,
            )
            raise NotOwnedByUserError

    def validate_items_qty_limit(self) -> None:
        if self.items_qty > self._config.restrictions.max_items_qty:
            logger.debug(
                "Cart %s. Max items qty limit exceeded! Limit %s, got %s",
                self.id,
                self._config.restrictions.max_items_qty,
                self.items_qty,
            )
            raise MaxItemsQtyLimitExceeded

    @contextmanager
    def _change_items(self) -> ContextManager[dict[int:CartItem]]:
        items_by_id = {item.id: item for item in self.items}
        yield items_by_id
        self.items = list(items_by_id.values())
