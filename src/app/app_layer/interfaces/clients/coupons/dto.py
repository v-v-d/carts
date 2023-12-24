from decimal import Decimal

from pydantic import BaseModel


class CouponOutputDTO(BaseModel):
    class Config:
        from_attributes = True

    min_cart_cost: Decimal | None = Decimal(500)  # hardcoded just for example
    discount_abs: Decimal | None = Decimal(300)  # hardcoded just for example
