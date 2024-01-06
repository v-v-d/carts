from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.domain.cart_items.value_objects import Qty


class AddItemToCartInputDTO(BaseModel):
    id: int
    qty: Qty
    auth_data: str
    cart_id: UUID


class ItemOutputDTO(BaseModel):
    class Config:
        from_attributes = True

    id: int
    name: str
    qty: Decimal
    price: Decimal
    cost: Decimal


class UpdateCartItemInputDTO(BaseModel):
    item_id: int
    cart_id: UUID
    qty: Qty
    auth_data: str


class DeleteCartItemInputDTO(BaseModel):
    item_id: int
    cart_id: UUID
    auth_data: str


class ClearCartInputDTO(BaseModel):
    cart_id: UUID
    auth_data: str
