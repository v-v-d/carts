from sqlalchemy import select

from app.domain.cart_coupons.dto import CartCouponDTO
from app.domain.cart_coupons.entities import CartCoupon
from app.domain.carts.entities import Cart
from app.infra.repositories.sqla import models
from app.infra.repositories.sqla.cart_coupons import CartCouponsRepository


class TestCartCouponsRepository(CartCouponsRepository):
    """
    Test repository for interactions with cart_coupons operations through database.
    """

    __test__ = False

    async def retrieve(self, cart: Cart) -> CartCoupon | None:
        stmt = select(models.CartCoupon).where(models.CartCoupon.cart_id == cart.id)
        row = await self._session.scalar(stmt)

        if not row:
            return

        return CartCoupon(
            data=CartCouponDTO(
                coupon_id=row.coupon_id,
                min_cart_cost=row.min_cart_cost,
                discount_abs=row.discount_abs,
            ),
            cart=cart,
        )
