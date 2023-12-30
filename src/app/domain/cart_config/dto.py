from decimal import Decimal

from pydantic import BaseModel


class CartConfigDTO(BaseModel):
    class Config:
        from_attributes = True

    max_items_qty: int
    min_cost_for_checkout: Decimal
    limit_items_by_id: dict[int, Decimal]
    hours_since_update_until_abandoned: int
    max_abandoned_notifications_qty: int
    abandoned_cart_text: str
