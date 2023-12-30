from abc import ABC, abstractmethod
from collections.abc import Mapping
from datetime import datetime
from uuid import UUID

from app.domain.cart_config.entities import CartConfig
from app.domain.carts.entities import Cart


class ICartsRepository(ABC):
    @abstractmethod
    async def create(self, cart: Cart) -> Cart:
        ...

    @abstractmethod
    async def retrieve(self, cart_id: UUID) -> Cart:
        ...

    @abstractmethod
    async def update(self, cart: Cart) -> Cart:
        ...

    @abstractmethod
    async def clear(self, cart_id: UUID) -> None:
        ...

    @abstractmethod
    async def get_list(self, page_size: int, created_at: datetime) -> list[Cart]:
        ...

    @abstractmethod
    async def get_config(self) -> CartConfig:
        ...

    @abstractmethod
    async def update_config(self, cart_config: CartConfig) -> CartConfig:
        ...

    @abstractmethod
    async def find_abandoned_cart_id_by_user_id(self) -> Mapping[UUID, int]:
        ...
