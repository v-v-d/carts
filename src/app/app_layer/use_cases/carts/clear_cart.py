from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.cart_items.dto import ClearCartInputDTO
from app.app_layer.interfaces.use_cases.carts.clear_cart import IClearCartUseCase
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class ClearCartUseCase(IClearCartUseCase):
    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, data: ClearCartInputDTO) -> CartOutputDTO:
        user = self._auth_system.get_user_data(auth_data=data.auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)
            cart.check_user_ownership(user_id=user.id)
            cart.clear()
            await self._uow.carts.clear(cart_id=cart.id)

        return CartOutputDTO.model_validate(cart)


class LockableClearCartUseCase(IClearCartUseCase):
    def __init__(
        self,
        use_case: IClearCartUseCase,
        distributed_lock_system: IDistributedLockSystem,
    ) -> None:
        self._use_case = use_case
        self._distributed_lock_system = distributed_lock_system

    async def execute(self, data: ClearCartInputDTO) -> CartOutputDTO:
        async with self._distributed_lock_system(name=str(data.cart_id)):
            return await self._use_case.execute(data=data)
