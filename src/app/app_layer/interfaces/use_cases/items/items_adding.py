from abc import ABC, abstractmethod
from uuid import UUID

from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.app_layer.interfaces.use_cases.items.dto import ItemAddingInputDTO


class IItemsAddingUseCase(ABC):
    @abstractmethod
    async def execute(self, cart_id: UUID, data: ItemAddingInputDTO) -> CartOutputDTO:
        ...
