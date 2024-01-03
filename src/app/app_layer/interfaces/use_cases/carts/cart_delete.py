from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.carts.dto import CartDeleteInputDTO, CartOutputDTO


class ICartDeleteUseCase(ABC):
    @abstractmethod
    async def execute(self, data: CartDeleteInputDTO) -> CartOutputDTO:
        ...
