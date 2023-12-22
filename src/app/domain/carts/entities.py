import uuid
from decimal import Decimal
from logging import getLogger

from app.config import CartConfig
from app.domain.cart_items.entities import CartItem
from app.domain.carts.dto import CartDTO
from app.domain.carts.exceptions import (
    CartItemDoesNotExistError,
    ChangeStatusError,
    MaxItemsQtyLimitExceeded,
    NotOwnedByUserError,
    OperationForbiddenError,
)
from app.domain.carts.value_objects import CartStatusEnum

logger = getLogger(__name__)


class Cart:
    STATUS_TRANSITION_RULESET: dict[
        CartStatusEnum, dict[CartStatusEnum, CartStatusEnum]
    ] = {
        CartStatusEnum.OPENED: {CartStatusEnum.DEACTIVATED, CartStatusEnum.LOCKED},
        CartStatusEnum.DEACTIVATED: {},
        CartStatusEnum.LOCKED: {CartStatusEnum.OPENED, CartStatusEnum.COMPLETED},
        CartStatusEnum.COMPLETED: {},
    }

    def __init__(self, data: CartDTO, items: list[CartItem], config: CartConfig) -> None:
        self.id = data.id
        self.user_id = data.user_id
        self.status = data.status
        self.items = items

        self._config = config

    @property
    def items_qty(self) -> Decimal:
        return sum(
            [
                self._config.weight_item_qty if item.is_weight else item.qty
                for item in self.items
            ]
        )

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
        self._check_can_be_modified(action="increase item qty")

        items_by_id = {item.id: item for item in self.items}
        items_by_id[item_id].qty += qty

        self._validate_items_qty_limit()

    def add_new_item(self, item: CartItem) -> None:
        self._check_can_be_modified(action="add new item")
        self.items.append(item)
        self._validate_items_qty_limit()

    def deactivate(self) -> None:
        self._validate_status_transition(new_status=CartStatusEnum.DEACTIVATED)
        self.status = CartStatusEnum.DEACTIVATED

    def get_item(self, item_id: int) -> CartItem:
        items_by_id = {item.id: item for item in self.items}

        if item_id not in items_by_id:
            logger.debug("Cart %s, item %s doesn't exist in cart.", self.id, item_id)
            raise CartItemDoesNotExistError

        return items_by_id[item_id]

    def update_item_qty(self, item_id: int, qty: Decimal) -> None:
        self._check_can_be_modified(action="update item qty")

        items_by_id = {item.id: item for item in self.items}
        items_by_id[item_id].qty = qty

        self._validate_items_qty_limit()

    def delete_item(self, item: CartItem) -> None:
        self._check_can_be_modified(action="delete item")

        items_by_id = {item.id: item for item in self.items}
        items_by_id.pop(item.id)
        self.items = list(items_by_id.values())

    def clear(self) -> None:
        self._check_can_be_modified(action="clear cart")
        self.items = []

    def check_user_ownership(self, user_id: int) -> None:
        if self.user_id != user_id:
            logger.debug(
                "Cart %s. Invalid user_id detected! Expected: %s, got: %s",
                self.id,
                self.user_id,
                user_id,
            )
            raise NotOwnedByUserError

    def _validate_items_qty_limit(self) -> None:
        if self.items_qty > self._config.restrictions.max_items_qty:
            logger.debug(
                "Cart %s. Max items qty limit exceeded! Limit: %s, got: %s",
                self.id,
                self._config.restrictions.max_items_qty,
                self.items_qty,
            )
            raise MaxItemsQtyLimitExceeded

    def _validate_status_transition(self, new_status: CartStatusEnum) -> None:
        if new_status not in self.STATUS_TRANSITION_RULESET[self.status]:
            logger.error(
                "Cart %s. Change status error! Expected: %s, got: %s",
                self.id,
                self.STATUS_TRANSITION_RULESET[self.status],
                new_status,
            )
            raise ChangeStatusError

    def _check_can_be_modified(self, action: str) -> None:
        if self.status != CartStatusEnum.OPENED:
            logger.error(
                f"Cart %s. Failed to {action} due to bad status! Expected: %s, actual: %s",
                self.id,
                CartStatusEnum.OPENED,
                self.status,
            )
            raise OperationForbiddenError
