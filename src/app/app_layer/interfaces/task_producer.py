from abc import ABC, abstractmethod


class ITaskProducer(ABC):
    @abstractmethod
    async def enqueue_example_task(self) -> None:
        ...
