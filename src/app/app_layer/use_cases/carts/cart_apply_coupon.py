from logging import getLogger

from app.app_layer.interfaces.auth_system.dto import UserDataOutputDTO
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.clients.coupons.client import ICouponsClient
from app.app_layer.interfaces.clients.coupons.dto import CouponOutputDTO
from app.app_layer.interfaces.clients.coupons.exceptions import CouponsClientError
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.carts.cart_apply_coupon import (
    ICartApplyCouponUseCase,
)
from app.app_layer.interfaces.use_cases.carts.dto import (
    CartApplyCouponInputDTO,
    CartOutputDTO,
)
from app.domain.cart_coupons.dto import CartCouponDTO
from app.domain.cart_coupons.entities import CartCoupon
from app.domain.carts.entities import Cart

logger = getLogger(__name__)


class CartApplyCouponUseCase(ICartApplyCouponUseCase):
    def __init__(
        self,
        uow: IUnitOfWork,
        coupons_client: ICouponsClient,
        auth_system: IAuthSystem,
    ) -> None:
        self._uow = uow
        self._coupons_client = coupons_client
        self._auth_system = auth_system

    async def execute(self, data: CartApplyCouponInputDTO) -> CartOutputDTO:
        user = self._auth_system.get_user_data(auth_data=data.auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)

        self._check_can_coupon_be_applied(user=user, cart=cart)

        coupon_data = await self._try_to_get_coupon_data(
            coupon_name=data.coupon_name,
            cart=cart,
        )
        self._apply_coupon_to_cart(cart=cart, data=data, coupon_data=coupon_data)

        async with self._uow(autocommit=True):
            await self._uow.cart_coupons.create(cart_coupon=cart.coupon)

        return CartOutputDTO.model_validate(cart)

    def _check_can_coupon_be_applied(self, user: UserDataOutputDTO, cart: Cart) -> None:
        self._check_user_ownership(cart=cart, user=user)
        cart.check_can_coupon_be_applied()

    def _check_user_ownership(self, cart: Cart, user: UserDataOutputDTO) -> None:
        if user.is_admin:
            return

        cart.check_user_ownership(user_id=user.id)

    async def _try_to_get_coupon_data(
        self, coupon_name: str, cart: Cart
    ) -> CouponOutputDTO:
        try:
            return await self._coupons_client.get_coupon(coupon_name=coupon_name)
        except CouponsClientError as err:
            logger.error(
                "Cart %s. Failed to get coupon %s data! Error: %s",
                cart.id,
                coupon_name,
                err,
            )
            raise

    def _apply_coupon_to_cart(
        self,
        cart: Cart,
        data: CartApplyCouponInputDTO,
        coupon_data: CouponOutputDTO,
    ) -> None:
        cart.set_coupon(
            coupon=CartCoupon(
                data=CartCouponDTO(
                    coupon_id=data.coupon_name,
                    min_cart_cost=coupon_data.min_cart_cost,
                    discount_abs=coupon_data.discount_abs,
                ),
                cart=cart,
            ),
        )


class LockableCartApplyCouponUseCase(ICartApplyCouponUseCase):
    def __init__(
        self,
        use_case: ICartApplyCouponUseCase,
        distributed_lock_system: IDistributedLockSystem,
    ) -> None:
        self._use_case = use_case
        self._distributed_lock_system = distributed_lock_system

    async def execute(self, data: CartApplyCouponInputDTO) -> CartOutputDTO:
        async with self._distributed_lock_system(name=f"cart-lock-{data.cart_id}"):
            return await self._use_case.execute(data=data)
