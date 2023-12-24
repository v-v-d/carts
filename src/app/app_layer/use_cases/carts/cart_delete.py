from uuid import UUID

from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.carts.cart_delete import ICartDeleteUseCase
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class CartDeleteUseCase(ICartDeleteUseCase):
    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, auth_data: str, cart_id: UUID) -> CartOutputDTO:
        user = self._auth_system.get_user_data(auth_data=auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=cart_id)
            cart.check_user_ownership(user_id=user.id)
            cart.deactivate()
            await self._uow.carts.update(cart=cart)

        return CartOutputDTO.model_validate(cart)


class LockableCartDeleteUseCase(ICartDeleteUseCase):
    def __init__(
        self,
        use_case: ICartDeleteUseCase,
        distributed_lock_system: IDistributedLockSystem,
    ) -> None:
        self._use_case = use_case
        self._distributed_lock_system = distributed_lock_system

    async def execute(self, auth_data: str, cart_id: UUID) -> CartOutputDTO:
        async with self._distributed_lock_system(name=str(cart_id)):
            return await self.execute(auth_data=auth_data, cart_id=cart_id)
