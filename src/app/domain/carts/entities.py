import uuid
from datetime import datetime
from decimal import Decimal
from logging import getLogger

from app.domain.cart_config.entities import CartConfig
from app.domain.cart_coupons.entities import CartCoupon
from app.domain.cart_items.entities import CartItem
from app.domain.carts.dto import CartDTO
from app.domain.carts.exceptions import (
    CantBeLockedError,
    CartItemAlreadyExistsError,
    CartItemDoesNotExistError,
    ChangeStatusError,
    CouponAlreadyAppliedError,
    CouponDoesNotExistError,
    MaxItemsQtyLimitExceeded,
    NotOwnedByUserError,
    OperationForbiddenError,
    SpecificItemQtyLimitExceeded,
)
from app.domain.carts.value_objects import CartStatusEnum

logger = getLogger(__name__)


class Cart:
    """
    Represents a shopping cart and provides methods to modify and manage the cart
    items, apply coupons, and change the cart status.
    """

    WEIGHT_ITEM_QTY: Decimal = Decimal(1)
    STATUS_TRANSITION_RULESET: dict[CartStatusEnum, set[CartStatusEnum]] = {
        CartStatusEnum.OPENED: {CartStatusEnum.DEACTIVATED, CartStatusEnum.LOCKED},
        CartStatusEnum.DEACTIVATED: {},
        CartStatusEnum.LOCKED: {CartStatusEnum.OPENED, CartStatusEnum.COMPLETED},
        CartStatusEnum.COMPLETED: {},
    }

    def __init__(
        self,
        data: CartDTO,
        items: list[CartItem],
        config: CartConfig,
        coupon: CartCoupon | None = None,
    ) -> None:
        self.created_at = data.created_at
        self.id = data.id
        self.user_id = data.user_id
        self.status = data.status
        self.items = items
        self.coupon = coupon

        self._config = config

    @property
    def items_qty(self) -> Decimal:
        return sum(
            [self.WEIGHT_ITEM_QTY if item.is_weight else item.qty for item in self.items]
        )

    @property
    def cost(self) -> Decimal:
        return sum([item.cost for item in self.items])

    @property
    def checkout_enabled(self) -> bool:
        return self.cost >= self._config.min_cost_for_checkout

    @classmethod
    def create(cls, user_id: int, config: CartConfig) -> "Cart":
        """Creates a new cart with the specified user ID and configuration."""

        return cls(
            data=CartDTO(
                created_at=datetime.now(),
                id=uuid.uuid4(),
                user_id=user_id,
                status=CartStatusEnum.OPENED,
            ),
            items=[],
            config=config,
        )

    def increase_item_qty(self, item_id: int, qty: Decimal) -> CartItem:
        """
        Increases the quantity of a specific item in the shopping cart. It checks if
        the cart can be modified, retrieves the item from the cart based on its ID,
        and then increases its quantity by the specified amount. It also validates the
        specific item quantity limit and the overall items quantity limit of the cart.
        """

        self._check_can_be_modified(action="increase item qty")

        items_by_id = {item.id: item for item in self.items}

        if item_id not in items_by_id:
            logger.info(
                "Cart %s. Failed to increase item %s qty! Item doesn't exist in cart.",
                self.id,
                item_id,
            )
            raise CartItemDoesNotExistError

        items_by_id[item_id].qty += qty

        self._check_specific_item_qty_limit(item=items_by_id[item_id])
        self._validate_items_qty_limit()

        return items_by_id[item_id]

    def add_new_item(self, item: CartItem) -> None:
        """
        Used to add a new item to the shopping cart. It checks if the cart can be
        modified, verifies if the item already exists in the cart, checks the
        specific item quantity limit and the overall items quantity limit of the cart,
        and then adds the item to the cart.
        """

        self._check_can_be_modified(action="add new item")

        items_by_id = {item.id: item for item in self.items}

        if item.id in items_by_id:
            logger.info(
                "Cart %s. Failed to add new item %s! Item already exists in cart.",
                self.id,
                item.id,
            )
            raise CartItemAlreadyExistsError

        self._check_specific_item_qty_limit(item=item)
        self.items.append(item)
        self._validate_items_qty_limit()

    def deactivate(self) -> None:
        """Used to change the status of a shopping cart to "DEACTIVATED"."""

        self._validate_status_transition(new_status=CartStatusEnum.DEACTIVATED)
        self.status = CartStatusEnum.DEACTIVATED

    def update_item_qty(self, item_id: int, qty: Decimal) -> CartItem:
        """
        Used to update the quantity of a specific item in the shopping cart. It checks
        if the cart can be modified, retrieves the item from the cart based on its ID,
        updates its quantity with the new value, and then validates the specific item
        quantity limit and the overall items quantity limit of the cart.
        """

        self._check_can_be_modified(action="update item qty")

        items_by_id = {item.id: item for item in self.items}

        if item_id not in items_by_id:
            logger.info(
                "Cart %s. Failed to update item %s! Item doesn't exist in cart.",
                self.id,
                item_id,
            )
            raise CartItemDoesNotExistError

        items_by_id[item_id].qty = qty

        self._check_specific_item_qty_limit(item=items_by_id[item_id])
        self._validate_items_qty_limit()

        return items_by_id[item_id]

    def delete_item(self, item_id: int) -> None:
        """
        Used to remove an item from the shopping cart. It checks if the cart can be
        modified, retrieves the item from the cart based on its ID, and then removes
        the item from the cart.
        """

        self._check_can_be_modified(action="delete item")

        items_by_id = {item.id: item for item in self.items}

        if item_id not in items_by_id:
            logger.info(
                "Cart %s. Failed to delete item %s! Item doesn't exist in cart.",
                self.id,
                item_id,
            )
            raise CartItemDoesNotExistError

        items_by_id.pop(item_id)
        self.items = list(items_by_id.values())

    def clear(self) -> None:
        """Used to remove all items from the shopping cart."""

        self._check_can_be_modified(action="clear cart")
        self.items = []

    def check_user_ownership(self, user_id: int) -> None:
        """
        Checks if the provided user_id matches the user_id of the cart. If they don't
        match, it raises a NotOwnedByUserError exception.
        """

        if self.user_id != user_id:
            logger.info(
                "Cart %s. Invalid user_id detected! Expected: %s, got: %s",
                self.id,
                self.user_id,
                user_id,
            )
            raise NotOwnedByUserError

    def check_can_coupon_be_applied(self) -> None:
        """
        Checks if a coupon can be applied to the shopping cart. It verifies if the
        cart can be modified, and if a coupon is already applied to the cart.
        """

        self._check_can_be_modified(action="apply coupon")

        if self.coupon is not None:
            logger.info(
                "Cart %s. Coupon %s already applied!",
                self.id,
                self.coupon.coupon_id,
            )
            raise CouponAlreadyAppliedError

    def set_coupon(self, coupon: CartCoupon) -> None:
        """Sets a coupon for a shopping cart."""

        self.coupon = coupon

    def remove_coupon(self) -> None:
        """
        Removes a coupon from the shopping cart. It checks if the cart can be modified,
        and if a coupon is currently applied to the cart. If a coupon exists, it is
        removed from the cart.
        """

        self._check_can_be_modified(action="remove coupon")

        if self.coupon is None:
            logger.info(
                "Cart %s. Failed to remove coupon! Coupon doesn't exist!", self.id
            )
            raise CouponDoesNotExistError

        self.coupon = None

    def lock(self) -> None:
        """
        Changes the status of a shopping cart to "LOCKED" if certain conditions are
        met. If the cart is not in the "OPENED" status, an error is raised.
        Additionally, if the checkout is disabled for the cart, another error is
        raised.
        """

        self._validate_status_transition(new_status=CartStatusEnum.LOCKED)

        if not self.checkout_enabled:
            logger.info("Cart %s. Failed to lock cart due to checkout disabled!", self.id)
            raise CantBeLockedError

        self.status = CartStatusEnum.LOCKED

    def unlock(self) -> None:
        """
        Changes the status of a shopping cart to "OPENED" if certain conditions are
        met.
        """

        self._validate_status_transition(new_status=CartStatusEnum.OPENED)
        self.status = CartStatusEnum.OPENED

    def complete(self) -> None:
        """
        Changes the status of a shopping cart to "COMPLETED" if certain conditions
        are met.
        """

        self._validate_status_transition(new_status=CartStatusEnum.COMPLETED)
        self.status = CartStatusEnum.COMPLETED

    def _check_specific_item_qty_limit(self, item: CartItem) -> None:
        if item.id not in self._config.limit_items_by_id:
            return

        if item.qty > self._config.limit_items_by_id[item.id]:
            logger.info(
                "Cart %s. Specific item %s qty limit exceeded! Limit: %s, got: %s",
                self.id,
                item.id,
                self._config.limit_items_by_id[item.id],
                item.qty,
            )
            raise SpecificItemQtyLimitExceeded(
                limit=self._config.limit_items_by_id[item.id],
                actual=item.qty,
            )

    def _validate_items_qty_limit(self) -> None:
        if self.items_qty > self._config.max_items_qty:
            logger.info(
                "Cart %s. Max items qty limit exceeded! Limit: %s, got: %s",
                self.id,
                self._config.max_items_qty,
                self.items_qty,
            )
            raise MaxItemsQtyLimitExceeded

    def _validate_status_transition(self, new_status: CartStatusEnum) -> None:
        if new_status not in self.STATUS_TRANSITION_RULESET[self.status]:
            logger.info(
                "Cart %s. Change status error! Expected: %s, got: %s",
                self.id,
                self.STATUS_TRANSITION_RULESET[self.status],
                new_status,
            )
            raise ChangeStatusError

    def _check_can_be_modified(self, action: str) -> None:
        if self.status != CartStatusEnum.OPENED:
            logger.info(
                f"Cart %s. Failed to {action} due to bad status! Expected: %s, actual: %s",
                self.id,
                CartStatusEnum.OPENED,
                self.status,
            )
            raise OperationForbiddenError
