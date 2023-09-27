from abc import ABC, abstractmethod

from app.interfaces.services.items.dto import ItemInputDTO, ItemOutputDTO


class IItemsService(ABC):
    @abstractmethod
    async def add_item(self, data: ItemInputDTO) -> ItemOutputDTO:
        ...

    @abstractmethod
    async def get_items(self) -> list[ItemOutputDTO]:
        ...
