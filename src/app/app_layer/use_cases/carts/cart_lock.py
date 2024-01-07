from logging import getLogger
from uuid import UUID

from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.use_cases.carts.dto import CartOutputDTO
from app.logging import update_context

logger = getLogger(__name__)


class LockCartUseCase:
    """
    Responsible for locking a cart by acquiring a distributed lock using the provided
    distributed lock system. It uses a unit of work to retrieve and update the cart's
    status.
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
        Executes the use case by acquiring a distributed lock and locking the cart.
        """

        await update_context(cart_id=cart_id)

        async with self._distributed_lock_system(name=f"cart-lock-{cart_id}"):
            return await self._lock_cart(cart_id=cart_id)

    async def _lock_cart(self, cart_id: UUID) -> CartOutputDTO:
        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=cart_id)
            cart.lock()
            await self._uow.carts.update(cart=cart)

        logger.info("Cart %s successfully locked", cart.id)

        return CartOutputDTO.model_validate(cart)
