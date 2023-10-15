from abc import ABC, abstractmethod

from app.app_layer.interfaces.services.items.dto import ItemListOutputDTO


class IItemsListService(ABC):
    @abstractmethod
    async def execute(self) -> list[ItemListOutputDTO]:
        ...
