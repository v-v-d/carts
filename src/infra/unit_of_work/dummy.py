from typing import Any

from app.interfaces.unit_of_work.sql import IUnitOfWork
from infra.repositories.items.dummy import ItemsRepository


class Uow(IUnitOfWork):
    def __init__(self, storage: dict[Any, Any]) -> None:
        self._storage = storage

    async def __aenter__(self) -> IUnitOfWork:
        self.items = ItemsRepository(self._storage)

        return await super().__aenter__()

    async def commit(self) -> None:
        print("This is dummy commit.")

    async def rollback(self) -> None:
        print("This is dummy rollback.")

    async def shutdown(self) -> None:
        print("This is dummy shutdown.")
