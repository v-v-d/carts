from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.cart_coupons.entities import CartCoupon


class ICartCouponsRepository(ABC):
    @abstractmethod
    async def create(self, cart_coupon: CartCoupon) -> CartCoupon:
        ...

    @abstractmethod
    async def delete(self, cart_id: UUID) -> None:
        ...
