from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.carts.dto import (
    CartOutputDTO,
    CartRetrieveInputDTO,
)


class ICartRetrieveUseCase(ABC):
    @abstractmethod
    async def execute(self, data: CartRetrieveInputDTO) -> CartOutputDTO:
        ...
