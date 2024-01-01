from abc import ABC, abstractmethod

from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart


class IItemsRepository(ABC):
    @abstractmethod
    async def add_item(self, item: CartItem) -> None:
        ...

    @abstractmethod
    async def update_item(self, item: CartItem) -> CartItem:
        ...

    @abstractmethod
    async def delete_item(self, cart: Cart, item_id: int) -> None:
        ...
