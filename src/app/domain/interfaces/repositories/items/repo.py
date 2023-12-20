from abc import ABC, abstractmethod

from app.domain.cart_items.entities import CartItem


class IItemsRepository(ABC):
    @abstractmethod
    async def add_item(self, item: CartItem) -> None:
        ...

    @abstractmethod
    async def update_item(self, item: CartItem) -> CartItem:
        ...

    @abstractmethod
    async def delete_item(self, item: CartItem) -> None:
        ...
