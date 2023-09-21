from abc import ABC, abstractmethod


class ITaskProducer(ABC):
    @abstractmethod
    async def enqueue_test_task(self) -> None:
        ...
