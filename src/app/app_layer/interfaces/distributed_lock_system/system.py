from abc import ABC, abstractmethod


class IDistributedLockSystem(ABC):
    def __call__(self, name: str, *args, **kwargs) -> "IDistributedLockSystem":
        self._name = name
        return self

    async def __aenter__(self) -> "IDistributedLockSystem":
        await self.acquire()
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.release()

    @abstractmethod
    async def acquire(self) -> None:
        ...

    @abstractmethod
    async def release(self) -> None:
        ...
