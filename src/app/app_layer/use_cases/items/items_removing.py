from decimal import Decimal

from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.app_layer.interfaces.use_cases.items.dto import ItemRemovingInputDTO
from app.app_layer.interfaces.use_cases.items.items_removing import IItemsRemovingUseCase
from app.domain.carts.entities import Cart
from app.domain.items.entities import Item
from app.domain.items.exceptions import QtyValidationError


class ItemsRemovingUseCase(IItemsRemovingUseCase):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, data: ItemRemovingInputDTO) -> CartOutputDTO:
        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)
            item = cart.get_item(data.item_id)
            cart = await self._decrease_item_qty_or_remove(cart=cart, item=item, qty=data.qty)

        return CartOutputDTO.model_validate(cart)

    async def _decrease_item_qty_or_remove(
        self,
        cart: Cart,
        item: Item,
        qty: Decimal,
    ) -> Cart:
        cart.decrease_item_qty(item_id=item.id, qty=qty)

        try:
            item.validate_qty()
        except QtyValidationError:
            cart = await self._remove_item_from_cart(cart=cart, item=item)
        else:
            await self._uow.items.update_item(item=item)

        return cart

    async def _remove_item_from_cart(self, cart: Cart, item: Item) -> Cart:
        cart.remove_item(item=item)
        await self._uow.items.remove_item(item=item)

        return cart
