from abc import ABC, abstractmethod
from uuid import UUID


class ITaskProducer(ABC):
    @abstractmethod
    async def enqueue_example_task(self, auth_data: str, cart_id: UUID) -> None:
        ...
