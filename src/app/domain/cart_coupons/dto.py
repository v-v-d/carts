from pydantic import BaseModel

from app.domain.cart_coupons.value_objects import CartCost, Discount


class CartCouponDTO(BaseModel):
    class Config:
        from_attributes = True

    coupon_id: str
    min_cart_cost: CartCost
    discount_abs: Discount
