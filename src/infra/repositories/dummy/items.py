from typing import Any

from app.interfaces.repositories.items import IItemsRepository
from domain.items.dto import ItemDTO
from domain.items.entities import Item


class ItemsRepository(IItemsRepository):
    def __init__(self, storage: dict[Any, Any]) -> None:
        self._storage = storage

    async def add_item(self, item: Item) -> None:
        self._storage[item.id] = {
            "id": item.id,
            "name": item.name,
            "qty": item.qty,
            "price": item.price,
        }

    async def get_items(self) -> list[Item]:
        return [Item(data=ItemDTO(**item)) for item in self._storage.values()]
