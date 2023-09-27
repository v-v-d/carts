from pydantic import TypeAdapter

from app.interfaces.clients.products.client import IProductsClient
from app.interfaces.services.items.dto import ItemInputDTO, ItemOutputDTO
from app.interfaces.services.items.service import IItemsService
from app.interfaces.unit_of_work.sql import IUnitOfWork
from domain.items.dto import ItemDTO
from domain.items.entities import Item


class ItemsService(IItemsService):
    def __init__(
        self,
        uow: IUnitOfWork,
        products_client: IProductsClient,
    ) -> None:
        self._uow = uow
        self._products_client = products_client

    async def add_item(self, data: ItemInputDTO) -> ItemOutputDTO:
        product = await self._products_client.get_product(data.id)
        item = Item(data=ItemDTO(id=data.id, qty=data.qty, name=product.title, price=product.price))

        async with self._uow(autocommit=True):
            await self._uow.items.add_item(item)

        return ItemOutputDTO.model_validate(item)

    async def get_items(self) -> list[ItemOutputDTO]:
        async with self._uow(autocommit=False):
            items = await self._uow.items.get_items()

        return TypeAdapter(list[ItemOutputDTO]).validate_python(items)
