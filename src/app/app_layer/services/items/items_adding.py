from logging import getLogger

from app.app_layer.interfaces.clients.products.client import IProductsClient
from app.app_layer.interfaces.clients.products.dto import ProductOutputDTO
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.app_layer.interfaces.repositories.items.exceptions import ItemAlreadyExists
from app.app_layer.interfaces.services.items.dto import ItemAddingInputDTO, ItemOutputDTO
from app.app_layer.interfaces.services.items.items_adding import IItemsAddingService
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.domain.items.dto import ItemDTO
from app.domain.items.entities import Item

logger = getLogger(__name__)


class ItemsAddingService(IItemsAddingService):
    def __init__(
        self,
        uow: IUnitOfWork,
        products_client: IProductsClient,
    ) -> None:
        self._uow = uow
        self._products_client = products_client

    async def execute(self, data: ItemAddingInputDTO) -> ItemOutputDTO:
        product = await self._try_to_get_product(data.id)

        item = Item(data=ItemDTO(id=data.id, qty=data.qty, name=product.title, price=product.price))
        item.validate_qty()

        await self._try_to_add_item(item)

        return ItemOutputDTO.model_validate(item)

    async def _try_to_get_product(self, product_id: int) -> ProductOutputDTO:
        try:
            return await self._products_client.get_product(product_id)
        except ProductsClientError as err:
            logger.error("Failed to add item %s! Error: %s", product_id, err)
            raise

    async def _try_to_add_item(self, item: Item) -> None:
        async with self._uow(autocommit=True):
            try:
                await self._uow.items.add_item(item)
            except ItemAlreadyExists as err:
                logger.error("Failed to add item %s, already exists! Error: %s", item.id, err)
                raise
