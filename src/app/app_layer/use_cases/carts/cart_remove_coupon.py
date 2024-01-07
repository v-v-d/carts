from logging import getLogger

from app.app_layer.interfaces.auth_system.dto import UserDataOutputDTO
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.use_cases.carts.dto import CartOutputDTO, CartRemoveCouponInputDTO
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import CouponDoesNotExistError
from app.logging import update_context

logger = getLogger(__name__)


class CartRemoveCouponUseCase:
    """
    Responsible for removing a coupon from a cart. It interacts with the IUnitOfWork,
    IAuthSystem, and IDistributedLockSystem interfaces to retrieve the cart, validate
    the user's ownership, remove the coupon, and update the cart.
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

    async def execute(self, data: CartRemoveCouponInputDTO) -> CartOutputDTO:
        """
        Executes the use case by retrieving the cart, validating the user's ownership,
        removing the coupon, and returning the updated cart.
        """

        await update_context(cart_id=data.cart_id)

        async with self._distributed_lock_system(name=f"cart-lock-{data.cart_id}"):
            return await self._remove_coupon(data=data)

    async def _remove_coupon(self, data: CartRemoveCouponInputDTO) -> CartOutputDTO:
        user = await self._auth_system.get_user_data(auth_data=data.auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)
            self._check_user_ownership(cart=cart, user=user)
            cart = await self._update_cart(cart=cart)

        logger.info("Coupon successfully deleted from cart %s", cart.id)

        return CartOutputDTO.model_validate(cart)

    def _check_user_ownership(self, cart: Cart, user: UserDataOutputDTO) -> None:
        if user.is_admin:
            return

        cart.check_user_ownership(user_id=user.id)

    async def _update_cart(self, cart: Cart) -> Cart:
        try:
            cart.remove_coupon()
        except CouponDoesNotExistError:
            return cart

        await self._uow.cart_coupons.delete(cart_id=cart.id)

        return cart
