from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.carts.dto import (
    CartApplyCouponInputDTO,
    CartOutputDTO,
)


class ICartApplyCouponUseCase(ABC):
    @abstractmethod
    async def execute(self, data: CartApplyCouponInputDTO) -> CartOutputDTO:
        ...
