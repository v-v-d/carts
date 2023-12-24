from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.domain.cart_items.value_objects import Qty


class ItemDTO(BaseModel):
    class Config:
        from_attributes = True

    id: int
    name: str
    qty: Qty
    price: Decimal
    is_weight: bool
    cart_id: UUID
