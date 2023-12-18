from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.cart_items.dto import CreateCartInputDTO
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class ICreateCartUseCase(ABC):
    @abstractmethod
    async def execute(self, data: CreateCartInputDTO) -> CartOutputDTO:
        ...
