from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.items.dto import ItemListOutputDTO


class IItemsListUseCase(ABC):
    @abstractmethod
    async def execute(self) -> list[ItemListOutputDTO]:
        ...
