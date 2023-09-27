from decimal import Decimal

from pydantic import BaseModel


class ItemDTO(BaseModel):
    id: int
    name: str
    qty: Decimal
    price: Decimal
