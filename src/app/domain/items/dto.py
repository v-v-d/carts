from decimal import Decimal

from pydantic import BaseModel


class ItemDTO(BaseModel):
    class Config:
        from_attributes = True

    id: int
    name: str
    qty: Decimal
    price: Decimal
    is_weight: bool
