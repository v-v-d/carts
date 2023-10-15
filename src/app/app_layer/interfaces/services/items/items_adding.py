from abc import ABC, abstractmethod

from app.app_layer.interfaces.services.items.dto import ItemAddingInputDTO, ItemAddingOutputDTO


class IItemsAddingService(ABC):
    @abstractmethod
    async def execute(self, data: ItemAddingInputDTO) -> ItemAddingOutputDTO:
        ...
