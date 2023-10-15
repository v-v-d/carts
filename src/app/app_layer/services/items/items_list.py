from pydantic import TypeAdapter

from app.app_layer.interfaces.services.items.dto import ItemListOutputDTO
from app.app_layer.interfaces.services.items.items_list import IItemsListService
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork


class ItemsListService(IItemsListService):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self) -> list[ItemListOutputDTO]:
        async with self._uow(autocommit=False):
            items = await self._uow.items.get_items()

        return TypeAdapter(list[ItemListOutputDTO]).validate_python(items)
