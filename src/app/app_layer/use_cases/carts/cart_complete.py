from uuid import UUID

from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.carts.cart_complete import ICompleteCartUseCase
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class CompleteCartUseCase(ICompleteCartUseCase):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, cart_id: UUID) -> CartOutputDTO:
        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=cart_id)
            cart.complete()
            await self._uow.carts.update(cart=cart)

        return CartOutputDTO.model_validate(cart)


class LockableCompleteCartUseCase(ICompleteCartUseCase):
    def __init__(
        self,
        use_case: ICompleteCartUseCase,
        distributed_lock_system: IDistributedLockSystem,
    ) -> None:
        self._use_case = use_case
        self._distributed_lock_system = distributed_lock_system

    async def execute(self, cart_id: UUID) -> CartOutputDTO:
        async with self._distributed_lock_system(name=f"cart-lock-{cart_id}"):
            return await self._use_case.execute(cart_id=cart_id)
