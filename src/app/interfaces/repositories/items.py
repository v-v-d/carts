from abc import ABC, abstractmethod

from domain.items.entities import Item


class IItemsRepository(ABC):
    @abstractmethod
    async def add_item(self, item: Item) -> None:
        ...

    @abstractmethod
    async def get_items(self) -> list[Item]:
        ...
