from abc import ABC, abstractmethod

from app.domain.interfaces.repositories.cart_coupons.repo import ICartCouponsRepository
from app.domain.interfaces.repositories.cart_notifications import (
    ICartNotificationsRepository,
)
from app.domain.interfaces.repositories.carts.repo import ICartsRepository
from app.domain.interfaces.repositories.items.repo import IItemsRepository


class IUnitOfWork(ABC):
    items: IItemsRepository
    carts: ICartsRepository
    cart_coupons: ICartCouponsRepository
    carts_notifications: ICartNotificationsRepository

    def __call__(self, autocommit: bool, *args, **kwargs) -> "IUnitOfWork":
        self._autocommit = autocommit

        return self

    async def __aenter__(self) -> "IUnitOfWork":
        return self  # pragma: no cover

    async def __aexit__(
        self, exc_type: type[BaseException] | None, *args, **kwargs
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
