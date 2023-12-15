from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ItemAddingInputDTO(BaseModel):
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


class ItemAddingOutputDTO(ItemOutputDTO):
    pass


class ItemListOutputDTO(ItemOutputDTO):
    pass


class ItemRemovingInputDTO(BaseModel):
    item_id: int
    cart_id: UUID
    qty: Decimal
