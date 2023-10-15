from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.infra.repositories.sqla.items import ItemsRepository


class Uow(IUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> IUnitOfWork:
        self._session = self._session_factory()

        self.items = ItemsRepository(self._session)

        return await super().__aenter__()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def shutdown(self) -> None:
        await self._session.close()
