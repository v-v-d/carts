from abc import ABC, abstractmethod
from uuid import UUID


class ITaskProducer(ABC):
    @abstractmethod
    async def enqueue_example_task(self, auth_data: str, cart_id: UUID) -> None:
        ...

    @abstractmethod
    async def enqueue_abandoned_cart_notification_task(
        self,
        user_id: int,
        cart_id: UUID,
    ) -> None:
        ...
