from pydantic import TypeAdapter

from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.items.dto import ItemListOutputDTO
from app.app_layer.interfaces.use_cases.items.items_list import IItemsListUseCase


class ItemsListUseCase(IItemsListUseCase):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self) -> list[ItemListOutputDTO]:
        async with self._uow(autocommit=False):
            items = await self._uow.items.get_items()

        return TypeAdapter(list[ItemListOutputDTO]).validate_python(items)
