from decimal import Decimal

from pydantic import BaseModel


class CartConfigOutputDTO(BaseModel):
    class Config:
        from_attributes = True

    max_items_qty: int
    min_cost_for_checkout: Decimal
    limit_items_by_id: dict[int, Decimal]


class CartConfigInputDTO(BaseModel):
    max_items_qty: int
    min_cost_for_checkout: Decimal
    limit_items_by_id: dict[int, Decimal]
    auth_data: str
