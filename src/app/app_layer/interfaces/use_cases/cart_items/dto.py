from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AddItemToCartInputDTO(BaseModel):
    id: int
    qty: Decimal


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


class DeleteCartItemInputDTO(BaseModel):
    item_id: int
    cart_id: UUID


class CreateCartInputDTO(BaseModel):
    user_id: int
