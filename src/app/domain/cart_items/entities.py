from decimal import Decimal

from app.domain.cart_items.dto import ItemDTO


class CartItem:
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
