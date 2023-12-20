from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.cart_items.dto import ClearCartInputDTO
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class IClearCartUseCase(ABC):
    @abstractmethod
    async def execute(self, data: ClearCartInputDTO) -> CartOutputDTO:
        ...
