from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AddItemToCartInputDTO(BaseModel):
    id: int
    qty: Decimal
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


class AddItemToCartOutputDTO(ItemOutputDTO):
    pass


class AddItemToCartListOutputDTO(ItemOutputDTO):
    pass


class UpdateCartItemInputDTO(BaseModel):
    item_id: int
    cart_id: UUID
    qty: Decimal
    auth_data: str


class DeleteCartItemInputDTO(BaseModel):
    item_id: int
    cart_id: UUID
    auth_data: str


class ClearCartInputDTO(BaseModel):
    cart_id: UUID
    auth_data: str
