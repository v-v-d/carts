from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.infra.repositories.sqla.cart_coupons import CartCouponsRepository
from app.infra.repositories.sqla.cart_notifications import CartsNotificationsRepository
from app.infra.repositories.sqla.carts import CartsRepository
from app.infra.repositories.sqla.items import ItemsRepository


class Uow(IUnitOfWork):
    """
    Provides a unit of work pattern for managing transactions and repositories in
    an asynchronous SQLAlchemy session.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

        # AsyncSession не подходит для многозадачности в асинхронных контекстах:
        # https://docs.sqlalchemy.org/en/20/orm/session_basics.html#is-the-session-thread-safe-is-asyncsession-safe-to-share-in-concurrent-tasks
        # Используем ContextVar, чтобы безопасно работать с одним объектом Uow
        # в операциях типа asyncio.gather(...).
        self._session_ctx: ContextVar[AsyncSession] = ContextVar("_sqla_session")

    async def __aenter__(self) -> IUnitOfWork:
        session = self._session_factory()
        self._session_ctx.set(session)

        self.items = ItemsRepository(session=session)
        self.carts = CartsRepository(session=session)
        self.cart_coupons = CartCouponsRepository(session=session)
        self.carts_notifications = CartsNotificationsRepository(session=session)

        return await super().__aenter__()

    async def commit(self) -> None:
        """
        Retrieves the current session from the context variable _sqla_session and calls
        the commit method on the session to commit the changes made in the session.
        """

        await self._session_ctx.get().commit()

    async def rollback(self) -> None:
        """
        Retrieves the current session from the context variable _sqla_session and calls
        the rollback method on the session to roll back the changes made in the session.
        """

        await self._session_ctx.get().rollback()

    async def shutdown(self) -> None:
        """
        Retrieves the current session from the context variable _sqla_session and Call
        the close method on the session to close it.
        """

        await self._session_ctx.get().close()
