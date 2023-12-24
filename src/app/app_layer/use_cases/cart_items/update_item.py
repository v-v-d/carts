from decimal import Decimal

from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.cart_items.dto import UpdateCartItemInputDTO
from app.app_layer.interfaces.use_cases.cart_items.update_item import (
    IUpdateCartItemUseCase,
)
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart


class UpdateCartItemUseCase(IUpdateCartItemUseCase):
    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, data: UpdateCartItemInputDTO) -> CartOutputDTO:
        user = self._auth_system.get_user_data(auth_data=data.auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)
            cart.check_user_ownership(user_id=user.id)
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
        await self._uow.items.update_item(item=item)

        return cart


class LockableUpdateCartItemUseCase(IUpdateCartItemUseCase):
    def __init__(
        self,
        use_case: IUpdateCartItemUseCase,
        distributed_lock_system: IDistributedLockSystem,
    ) -> None:
        self._use_case = use_case
        self._distributed_lock_system = distributed_lock_system

    async def execute(self, data: UpdateCartItemInputDTO) -> CartOutputDTO:
        async with self._distributed_lock_system(name=str(data.cart_id)):
            return await self._use_case.execute(data=data)
