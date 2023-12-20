from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.domain.carts.value_objects import CartStatusEnum


class ItemOutputDTO(BaseModel):
    class Config:
        from_attributes = True

    id: int
    name: str
    qty: Decimal
    price: Decimal
    cost: Decimal
    is_weight: bool


class CartOutputDTO(BaseModel):
    class Config:
        from_attributes = True

    id: UUID
    user_id: int
    status: CartStatusEnum
    items: list[ItemOutputDTO]
    items_qty: Decimal
    cost: Decimal
