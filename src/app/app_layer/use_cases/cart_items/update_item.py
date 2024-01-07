from logging import getLogger

from app.app_layer.interfaces.auth_system.dto import UserDataOutputDTO
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.use_cases.cart_items.dto import UpdateCartItemInputDTO
from app.app_layer.use_cases.carts.dto import CartOutputDTO
from app.domain.carts.entities import Cart
from app.logging import update_context

logger = getLogger(__name__)


class UpdateCartItemUseCase:
    """
    Responsible for updating the quantity of an item in a cart. It uses an instance
    of IUnitOfWork to manage the database transactions, an instance of IAuthSystem to
    validate the user's authentication data, and an instance of IDistributedLockSystem
    to acquire a lock on the cart during the update process.
    """

    def __init__(
        self,
        uow: IUnitOfWork,
        auth_system: IAuthSystem,
        distributed_lock_system: IDistributedLockSystem,
    ) -> None:
        self._uow = uow
        self._auth_system = auth_system
        self._distributed_lock_system = distributed_lock_system

    async def execute(self, data: UpdateCartItemInputDTO) -> CartOutputDTO:
        """
        Executes the update cart item use case. Acquires a lock on the cart, validates
        the user's authentication data, retrieves the cart, checks user ownership,
        updates the item quantity, and returns the updated cart.
        """

        await update_context(cart_id=data.cart_id)

        async with self._distributed_lock_system(name=f"cart-lock-{data.cart_id}"):
            return await self._update_cart_item(data=data)

    async def _update_cart_item(self, data: UpdateCartItemInputDTO) -> CartOutputDTO:
        user = await self._auth_system.get_user_data(auth_data=data.auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)
            self._check_user_ownership(cart=cart, user=user)
            cart = await self._update_item_qty(cart=cart, data=data)

        return CartOutputDTO.model_validate(cart)

    def _check_user_ownership(self, cart: Cart, user: UserDataOutputDTO) -> None:
        if user.is_admin:
            return

        cart.check_user_ownership(user_id=user.id)

    async def _update_item_qty(
        self,
        cart: Cart,
        data: UpdateCartItemInputDTO,
    ) -> Cart:
        item = cart.update_item_qty(item_id=data.item_id, qty=data.qty)
        await self._uow.items.update_item(item=item)

        logger.info(
            "Cart %s. Item %s successfully updated with qty %s",
            cart.id,
            item.id,
            data.qty,
        )

        return cart
