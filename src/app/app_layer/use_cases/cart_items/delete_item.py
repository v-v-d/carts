from app.app_layer.interfaces.auth_system.dto import UserDataOutputDTO
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.cart_items.delete_item import (
    IDeleteCartItemUseCase,
)
from app.app_layer.interfaces.use_cases.cart_items.dto import DeleteCartItemInputDTO
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import CartItemDoesNotExistError


class DeleteCartItemUseCase(IDeleteCartItemUseCase):
    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, data: DeleteCartItemInputDTO) -> CartOutputDTO:
        user = self._auth_system.get_user_data(auth_data=data.auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)
            self._check_item_can_be_deleted(cart=cart, user=user)
            cart = await self._update_cart(cart=cart, data=data)

        return CartOutputDTO.model_validate(cart)

    def _check_item_can_be_deleted(self, cart: Cart, user: UserDataOutputDTO) -> None:
        self._check_user_ownership(cart=cart, user=user)
        cart.check_item_can_be_deleted()

    def _check_user_ownership(self, cart: Cart, user: UserDataOutputDTO) -> None:
        if user.is_admin:
            return

        cart.check_user_ownership(user_id=user.id)

    async def _update_cart(self, cart: Cart, data: DeleteCartItemInputDTO) -> Cart:
        try:
            item = cart.get_item(data.item_id)
        except CartItemDoesNotExistError:
            return cart

        return await self._delete_item_from_cart(cart=cart, item=item)

    async def _delete_item_from_cart(self, cart: Cart, item: CartItem) -> Cart:
        cart.delete_item(item=item)
        await self._uow.items.delete_item(item=item)

        return cart


class LockableDeleteCartItemUseCase(IDeleteCartItemUseCase):
    def __init__(
        self,
        use_case: IDeleteCartItemUseCase,
        distributed_lock_system: IDistributedLockSystem,
    ) -> None:
        self._use_case = use_case
        self._distributed_lock_system = distributed_lock_system

    async def execute(self, data: DeleteCartItemInputDTO) -> CartOutputDTO:
        async with self._distributed_lock_system(name=f"cart-lock-{data.cart_id}"):
            return await self._use_case.execute(data=data)
