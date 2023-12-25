from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.carts.dto import CartListInputDTO, CartListOutputDTO


class ICartListUseCase(ABC):
    @abstractmethod
    async def execute(self, data: CartListInputDTO) -> CartListOutputDTO:
        ...
