from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.cart_items.dto import DeleteCartItemInputDTO
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class IDeleteCartItemUseCase(ABC):
    @abstractmethod
    async def execute(self, data: DeleteCartItemInputDTO) -> CartOutputDTO:
        ...
