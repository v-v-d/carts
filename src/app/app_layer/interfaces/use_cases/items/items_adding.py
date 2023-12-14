from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.items.dto import ItemAddingInputDTO, ItemAddingOutputDTO


class IItemsAddingUseCase(ABC):
    @abstractmethod
    async def execute(self, data: ItemAddingInputDTO) -> ItemAddingOutputDTO:
        ...
