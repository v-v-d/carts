from decimal import Decimal
from logging import getLogger

from app.domain.items.dto import ItemDTO
from app.domain.items.exceptions import QtyValidationError

logger = getLogger(__name__)


class Item:
    min_valid_qty: int = 1
    price_precision: int = 10
    price_scale: int = 2

    def __init__(self, data: ItemDTO) -> None:
        self.id = data.id
        self.name = data.name
        self.qty = data.qty
        self.price = data.price
        self.is_weight = data.is_weight
        self.cart_id = data.cart_id

    @property
    def cost(self) -> Decimal:
        return self.price * self.qty

    def validate_qty(self) -> None:
        if self.qty < self.min_valid_qty:
            logger.info(
                "Invalid item %s qty detected! Required >= %s, got %s.",
                self.id,
                self.min_valid_qty,
                self.qty,
            )
            raise QtyValidationError
