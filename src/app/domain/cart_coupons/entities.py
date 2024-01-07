import typing
from decimal import Decimal

from app.domain.cart_coupons.dto import CartCouponDTO

if typing.TYPE_CHECKING:  # pragma: no cover
    from app.domain.carts.entities import Cart


class CartCoupon:
    """
    Represents a coupon that can be applied to a shopping cart. It calculates the
    discounted cart cost and checks if the coupon is applied.
    """

    def __init__(self, data: CartCouponDTO, cart: "Cart") -> None:
        self.coupon_id = data.coupon_id
        self.min_cart_cost = data.min_cart_cost
        self.discount_abs = data.discount_abs
        self.cart = cart

    @property
    def cart_cost(self) -> Decimal:
        return self.cart.cost - self.discount_abs

    @property
    def applied(self) -> bool:
        return self.cart.cost >= self.min_cart_cost
