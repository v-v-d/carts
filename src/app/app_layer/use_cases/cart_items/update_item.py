from decimal import Decimal

from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.cart_items.dto import UpdateCartItemInputDTO
from app.app_layer.interfaces.use_cases.cart_items.update_item import IUpdateCartItemUseCase
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.domain.cart_items.entities import CartItem
from app.domain.cart_items.exceptions import MinQtyLimitExceededError
from app.domain.carts.entities import Cart


class UpdateCartItemUseCase(IUpdateCartItemUseCase):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, data: UpdateCartItemInputDTO) -> CartOutputDTO:
        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)
            item = cart.get_item(data.item_id)
            cart = await self._update_item_qty(cart=cart, item=item, new_qty=data.qty)

        return CartOutputDTO.model_validate(cart)

    async def _update_item_qty(
        self,
        cart: Cart,
        item: CartItem,
        new_qty: Decimal,
    ) -> Cart:
        cart.update_item_qty(item_id=item.id, qty=new_qty)

        try:
            item.check_item_qty_above_min()
        except MinQtyLimitExceededError:
            return await self._delete_item_from_cart(cart=cart, item=item)

        await self._uow.items.update_item(item=item)

        return cart

    async def _delete_item_from_cart(self, cart: Cart, item: CartItem) -> Cart:
        cart.delete_item(item=item)
        await self._uow.items.delete_item(item=item)

        return cart