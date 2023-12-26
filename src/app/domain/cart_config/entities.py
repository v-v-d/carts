from decimal import Decimal

from app.domain.cart_config.dto import CartConfigDTO


class CartConfig:
    def __init__(self, data: CartConfigDTO) -> None:
        self.data = data

    @property
    def max_items_qty(self) -> int:
        return self.data.max_items_qty

    @property
    def min_cost_for_checkout(self) -> Decimal:
        return self.data.min_cost_for_checkout

    @property
    def limit_items_by_id(self) -> dict[int, Decimal]:
        return self.data.limit_items_by_id
