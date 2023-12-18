from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.app_layer.interfaces.use_cases.cart_items.dto import UpdateCartItemInputDTO


class IUpdateCartItemUseCase(ABC):
    @abstractmethod
    async def execute(self, data: UpdateCartItemInputDTO) -> CartOutputDTO:
        ...
