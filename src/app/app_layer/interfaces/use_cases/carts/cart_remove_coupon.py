from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.carts.dto import (
    CartOutputDTO,
    CartRemoveCouponInputDTO,
)


class ICartRemoveCouponUseCase(ABC):
    @abstractmethod
    async def execute(self, data: CartRemoveCouponInputDTO) -> CartOutputDTO:
        ...
