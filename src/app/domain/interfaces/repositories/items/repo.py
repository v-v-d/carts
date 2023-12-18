from abc import ABC, abstractmethod

from app.domain.items.entities import Item


class IItemsRepository(ABC):
    @abstractmethod
    async def add_item(self, item: Item) -> None:
        ...

    @abstractmethod
    async def get_items(self) -> list[Item]:
        ...

    @abstractmethod
    async def update_item(self, item: Item) -> Item:
        ...

    @abstractmethod
    async def delete_item(self, item: Item) -> None:
        ...
