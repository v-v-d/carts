from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator

from app.app_layer.use_cases.carts.dto import CartOutputDTO
from app.domain.carts.value_objects import CartStatusEnum


class ItemViewModel(BaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True

    id: int
    name: str
    qty: float
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

    created_at: datetime
    id: UUID
    user_id: int
    status: CartStatusEnum
    items: list[ItemViewModel]
    items_qty: float
    cost: float
    checkout_enabled: bool
    coupon: CartCouponViewModel | None = None


class CartListViewModel(BaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True

    items: list[CartViewModel]
    page_size: int
    next_page: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def _set_next_page(
        cls,
        data: dict[str, list[CartOutputDTO] | int | datetime],
    ) -> dict[str, list[CartOutputDTO] | int | datetime]:
        if not data["items"]:
            return data

        last_item = data["items"][-1]
        data["next_page"] = last_item.created_at

        return data


class CartConfigModelView(BaseModel):
    class Config:
        from_attributes = True

    max_items_qty: int
    min_cost_for_checkout: int
    limit_items_by_id: dict[int, int]
    hours_since_update_until_abandoned: int
    max_abandoned_notifications_qty: int
    abandoned_cart_text: str
