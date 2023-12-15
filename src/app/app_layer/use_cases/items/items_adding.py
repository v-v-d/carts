from decimal import Decimal
from logging import getLogger
from uuid import UUID

from app.app_layer.interfaces.clients.products.client import IProductsClient
from app.app_layer.interfaces.clients.products.dto import ProductOutputDTO
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.app_layer.interfaces.use_cases.items.dto import ItemAddingInputDTO
from app.app_layer.interfaces.use_cases.items.items_adding import IItemsAddingUseCase
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import ItemDoesNotExistInCartError
from app.domain.items.dto import ItemDTO
from app.domain.items.entities import Item

logger = getLogger(__name__)


class ItemsAddingUseCase(IItemsAddingUseCase):
    def __init__(
        self,
        uow: IUnitOfWork,
        products_client: IProductsClient,
    ) -> None:
        self._uow = uow
        self._products_client = products_client

    async def execute(self, cart_id: UUID, data: ItemAddingInputDTO) -> CartOutputDTO:
        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=cart_id)

        try:
            item = cart.get_item(data.id)
        except ItemDoesNotExistInCartError:
            cart = await self._try_to_add_new_item_to_cart(cart=cart, data=data)
        else:
            cart = await self._increase_item_qty(cart=cart, item=item, qty=data.qty)

        return CartOutputDTO.model_validate(cart)

    async def _increase_item_qty(self, cart: Cart, item: Item, qty: Decimal) -> Cart:
        cart.increase_item_qty(item_id=item.id, qty=qty)

        async with self._uow(autocommit=True):
            await self._uow.items.update_item(item=item)

        return cart

    async def _try_to_add_new_item_to_cart(
        self,
        cart: Cart,
        data: ItemAddingInputDTO,
    ) -> Cart:
        item = await self._try_to_create_item(cart=cart, data=data)
        cart.add_new_item(item)

        async with self._uow(autocommit=True):
            await self._uow.items.add_item(item=item)

        return cart

    async def _try_to_create_item(self, cart: Cart, data: ItemAddingInputDTO) -> Item:
        product = await self._try_to_get_product(data.id)

        item = Item(
            data=ItemDTO(
                id=data.id,
                qty=data.qty,
                name=product.title,
                price=product.price,
                is_weight=False,  # hardcoded just for example
                cart_id=cart.id,
            ),
        )
        item.validate_qty()

        return item

    async def _try_to_get_product(self, product_id: int) -> ProductOutputDTO:
        try:
            return await self._products_client.get_product(product_id)
        except ProductsClientError as err:
            logger.error("Failed to add item %s! Error: %s", product_id, err)
            raise
