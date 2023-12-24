from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.carts.cart_remove_coupon import (
    ICartRemoveCouponUseCase,
)
from app.app_layer.interfaces.use_cases.carts.dto import (
    CartOutputDTO,
    CartRemoveCouponInputDTO,
)
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import CouponDoesNotExistError


class CartRemoveCouponUseCase(ICartRemoveCouponUseCase):
    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, data: CartRemoveCouponInputDTO) -> CartOutputDTO:
        user = self._auth_system.get_user_data(auth_data=data.auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)
            cart.check_user_ownership(user_id=user.id)
            cart = await self._update_cart(cart=cart)

        return CartOutputDTO.model_validate(cart)

    async def _update_cart(self, cart: Cart) -> Cart:
        try:
            cart.remove_coupon()
        except CouponDoesNotExistError:
            return cart

        await self._uow.cart_coupons.delete(cart_id=cart.id)

        return cart


class LockableCartRemoveCouponUseCase(ICartRemoveCouponUseCase):
    def __init__(
        self,
        use_case: ICartRemoveCouponUseCase,
        distributed_lock_system: IDistributedLockSystem,
    ) -> None:
        self._use_case = use_case
        self._distributed_lock_system = distributed_lock_system

    async def execute(self, data: CartRemoveCouponInputDTO) -> CartOutputDTO:
        async with self._distributed_lock_system(name=str(data.cart_id)):
            return await self._use_case.execute(data=data)
