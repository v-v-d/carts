from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.app_layer.interfaces.use_cases.items.dto import ItemRemovingInputDTO


class IItemsRemovingUseCase(ABC):
    @abstractmethod
    async def execute(self, data: ItemRemovingInputDTO) -> CartOutputDTO:
        ...
