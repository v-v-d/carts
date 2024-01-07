from logging import getLogger
from uuid import UUID

from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.use_cases.carts.dto import CartOutputDTO
from app.logging import update_context

logger = getLogger(__name__)


class UnlockCartUseCase:
    """
    Responsible for unlocking a cart by changing its status from "LOCKED" to "OPENED"
    in the application. It uses a distributed lock system to ensure that only one
    process can access the cart at a time.
    """

    def __init__(
        self,
        uow: IUnitOfWork,
        distributed_lock_system: IDistributedLockSystem,
    ) -> None:
        self._uow = uow
        self._distributed_lock_system = distributed_lock_system

    async def execute(self, cart_id: UUID) -> CartOutputDTO:
        """
        Executes the use case by unlocking the cart with the given cart_id. It first
        updates the context with the cart_id, then acquires a lock on the cart using
        the distributed lock system. After acquiring the lock, it unlocks the cart and
        update it in the unit of work. Finally, it returns the unlocked cart as a
        CartOutputDTO object.
        """

        await update_context(cart_id=cart_id)

        async with self._distributed_lock_system(name=f"cart-lock-{cart_id}"):
            return await self._unlock_cart(cart_id=cart_id)

    async def _unlock_cart(self, cart_id: UUID) -> CartOutputDTO:
        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=cart_id)
            cart.unlock()
            await self._uow.carts.update(cart=cart)

        logger.info("Cart %s successfully unlocked", cart.id)

        return CartOutputDTO.model_validate(cart)
