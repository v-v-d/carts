from abc import ABC, abstractmethod

from app.app_layer.interfaces.repositories.items.repo import IItemsRepository


class IUnitOfWork(ABC):
    items: IItemsRepository

    def __call__(self, autocommit: bool, *args, **kwargs) -> "IUnitOfWork":
        self._autocommit = autocommit

        return self

    async def __aenter__(self) -> "IUnitOfWork":
        return self  # pragma: no cover

    async def __aexit__(self, exc_type: type[BaseException] | None, *args, **kwargs) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            if self._autocommit:
                await self.commit()

        await self.shutdown()

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        ...
