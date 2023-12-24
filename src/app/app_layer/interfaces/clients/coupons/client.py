from abc import ABC, abstractmethod

from app.app_layer.interfaces.clients.coupons.dto import CouponOutputDTO


class ICouponsClient(ABC):
    @abstractmethod
    async def get_coupon(self, coupon_name: str) -> CouponOutputDTO:
        ...
