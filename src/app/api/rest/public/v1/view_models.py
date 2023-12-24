from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.carts.value_objects import CartStatusEnum


class ItemViewModel(BaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True

    id: int
    name: str = Field(alias="title")
    qty: float = Field(alias="quantity")
    price: float
    cost: float
    is_weight: bool


class CartCouponViewModel(BaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True

    coupon_id: str
    discount_abs: float
    cart_cost: float
    applied: bool


class CartViewModel(BaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True

    id: UUID
    user_id: int
    status: CartStatusEnum
    items: list[ItemViewModel]
    items_qty: float = Field(alias="items_quantity")
    cost: float
    checkout_enabled: bool
    coupon: CartCouponViewModel | None = None
