from abc import ABC, abstractmethod
from uuid import UUID

from app.config import TaskConfig


class IAbandonedCartsService(ABC):
    @property
    @abstractmethod
    def config(self) -> TaskConfig:
        ...

    @abstractmethod
    async def process_abandoned_carts(self) -> None:
        ...

    @abstractmethod
    async def send_notification(self, user_id: int, cart_id: UUID) -> None:
        ...
