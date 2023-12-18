from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.cart_items.dto import UpdateCartItemInputDTO
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class IUpdateCartItemUseCase(ABC):
    @abstractmethod
    async def execute(self, data: UpdateCartItemInputDTO) -> CartOutputDTO:
        ...
