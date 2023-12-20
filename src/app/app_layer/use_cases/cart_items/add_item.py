from decimal import Decimal
from logging import getLogger

from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.clients.products.client import IProductsClient
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.cart_items.add_item import IAddCartItemUseCase
from app.app_layer.interfaces.use_cases.cart_items.dto import AddItemToCartInputDTO
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.domain.cart_items.dto import ItemDTO
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import CartItemDoesNotExistError

logger = getLogger(__name__)


class AddCartItemUseCase(IAddCartItemUseCase):
    def __init__(
        self,
        uow: IUnitOfWork,
        products_client: IProductsClient,
        auth_system: IAuthSystem,
    ) -> None:
        self._uow = uow
        self._products_client = products_client
        self._auth_system = auth_system

    async def execute(self, data: AddItemToCartInputDTO) -> CartOutputDTO:
        user = self._auth_system.get_user_data(auth_data=data.auth_data)
        CartItem.check_qty_above_min(data.qty)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)

        cart.check_user_ownership(user_id=user.id)
        cart = await self._update_cart(cart=cart, data=data)

        return CartOutputDTO.model_validate(cart)

    async def _update_cart(self, cart: Cart, data: AddItemToCartInputDTO) -> Cart:
        try:
            item = cart.get_item(data.id)
        except CartItemDoesNotExistError:
            return await self._try_to_add_new_item_to_cart(cart=cart, data=data)

        return await self._increase_item_qty(cart=cart, item=item, qty=data.qty)

    async def _try_to_add_new_item_to_cart(
        self,
        cart: Cart,
        data: AddItemToCartInputDTO,
    ) -> Cart:
        item = await self._try_to_create_item(cart=cart, data=data)
        cart.add_new_item(item)

        async with self._uow(autocommit=True):
            await self._uow.items.add_item(item=item)

        return cart

    async def _try_to_create_item(self, cart: Cart, data: AddItemToCartInputDTO) -> CartItem:
        try:
            product = await self._products_client.get_product(item_id=data.id)
        except ProductsClientError as err:
            logger.error(
                "Cart %s, item %s. Failed to get product data! Error: %s",
                cart.id,
                data.id,
                err,
            )
            raise

        return CartItem(
            data=ItemDTO(
                id=data.id,
                qty=data.qty,
                name=product.title,
                price=product.price,
                is_weight=False,  # hardcoded just for example
                cart_id=cart.id,
            ),
        )

    async def _increase_item_qty(self, cart: Cart, item: CartItem, qty: Decimal) -> Cart:
        cart.increase_item_qty(item_id=item.id, qty=qty)

        async with self._uow(autocommit=True):
            await self._uow.items.update_item(item=item)

        return cart
