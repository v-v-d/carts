from abc import ABC, abstractmethod
from types import TracebackType

from app.interfaces.repositories.items import IItemsRepository


class IUnitOfWork(ABC):
    items: IItemsRepository

    def __call__(self, autocommit: bool, *args, **kwargs) -> "IUnitOfWork":
        self._autocommit = autocommit

        return self

    async def __aenter__(self) -> "IUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType,
    ) -> None:
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
