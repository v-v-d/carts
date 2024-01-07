from logging import getLogger
from uuid import UUID

from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.use_cases.carts.dto import CartOutputDTO
from app.logging import update_context

logger = getLogger(__name__)


class CompleteCartUseCase:
    """
    Responsible for completing a cart by updating its status to "completed" in the
    database. It uses a distributed lock system to ensure that only one process can
    change the cart at a time.
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
        Executes the complete cart use case by updating the cart's status to
        "completed" in the database. It also updates the context with the cart ID and
        acquires a distributed lock to ensure exclusive access to the cart.
        """

        await update_context(cart_id=cart_id)

        async with self._distributed_lock_system(name=f"cart-lock-{cart_id}"):
            return await self._complete_cart(cart_id=cart_id)

    async def _complete_cart(self, cart_id: UUID) -> CartOutputDTO:
        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=cart_id)
            cart.complete()
            await self._uow.carts.update(cart=cart)

        logger.info("Cart %s successfully completed", cart.id)

        return CartOutputDTO.model_validate(cart)
