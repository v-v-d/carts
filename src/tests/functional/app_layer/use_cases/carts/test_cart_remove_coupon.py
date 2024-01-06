from unittest.mock import ANY, AsyncMock

import pytest

from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.use_cases.carts.cart_remove_coupon import CartRemoveCouponUseCase
from app.app_layer.use_cases.carts.dto import CartRemoveCouponInputDTO
from app.config import RedisLockConfig
from app.domain.cart_coupons.entities import CartCoupon
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import NotOwnedByUserError
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError
from tests.environment.unit_of_work import TestUow
from tests.utils import fake


@pytest.fixture()
async def cart(cart: Cart, coupon: CartCoupon, uow: TestUow) -> Cart:
    cart.set_coupon(coupon=coupon)

    async with uow(autocommit=True):
        await uow.cart_coupons.create(cart_coupon=coupon)

    return cart


@pytest.fixture()
def use_case(
    uow: TestUow,
    auth_system: IAuthSystem,
    distributed_lock_system: IDistributedLockSystem,
) -> CartRemoveCouponUseCase:
    return CartRemoveCouponUseCase(
        uow=uow,
        auth_system=auth_system,
        distributed_lock_system=distributed_lock_system,
    )


@pytest.fixture()
def dto(cart: Cart, auth_data: str) -> CartRemoveCouponInputDTO:
    return CartRemoveCouponInputDTO(auth_data=auth_data, cart_id=cart.id)


@pytest.mark.parametrize("cart", [{"user_id": 1}], indirect=True)
async def test_ok(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartRemoveCouponUseCase,
    dto: CartRemoveCouponInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    result = await use_case.execute(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=cart.id)
        coupon = await uow.cart_coupons.retrieve(cart=cart)

    assert coupon is None
    assert result.coupon is None
    assert cart.coupon is None

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )


@pytest.mark.parametrize("cart", [{"user_id": 1}], indirect=True)
async def test_coupon_not_found(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartRemoveCouponUseCase,
    dto: CartRemoveCouponInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    for _ in range(2):
        result = await use_case.execute(data=dto)
        assert result.coupon is None

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=cart.id)
        coupon = await uow.cart_coupons.retrieve(cart=cart)

    assert coupon is None
    assert cart.coupon is None

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )


async def test_remove_coupon_by_admin(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartRemoveCouponUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    result = await use_case.execute(
        data=CartRemoveCouponInputDTO(
            auth_data="Bearer admin.1",
            cart_id=cart.id,
        )
    )

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=cart.id)
        coupon = await uow.cart_coupons.retrieve(cart=cart)

    assert coupon is None
    assert result.coupon is None
    assert cart.coupon is None

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )


@pytest.mark.parametrize("redis", [{"returns": False}], indirect=True)
async def test_cart_already_locked_for_updates(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartRemoveCouponUseCase,
    dto: CartRemoveCouponInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(AlreadyLockedError, match=""):
        await use_case.execute(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=cart.id)
        coupon = await uow.cart_coupons.retrieve(cart=cart)

    assert coupon is not None
    assert cart.coupon is not None

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )


async def test_invalid_auth_data(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartRemoveCouponUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(InvalidAuthDataError, match=""):
        await use_case.execute(
            data=CartRemoveCouponInputDTO(
                auth_data="INVALID AUTH DATA",
                cart_id=cart.id,
            ),
        )

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=cart.id)
        coupon = await uow.cart_coupons.retrieve(cart=cart)

    assert coupon is not None
    assert cart.coupon is not None

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )


async def test_cart_not_found(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartRemoveCouponUseCase,
) -> None:
    cart_id = fake.cryptographic.uuid_object()

    with pytest.raises(CartNotFoundError, match=""):
        await use_case.execute(
            data=CartRemoveCouponInputDTO(
                auth_data="Bearer customer.1",
                cart_id=cart_id,
            ),
        )

    redis.set.assert_awaited_with(
        f"cart-lock-{cart_id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )


async def test_not_owned_by_current_user(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartRemoveCouponUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(NotOwnedByUserError, match=""):
        await use_case.execute(
            data=CartRemoveCouponInputDTO(
                auth_data="Bearer customer.2",
                cart_id=cart.id,
            ),
        )

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=cart.id)
        coupon = await uow.cart_coupons.retrieve(cart=cart)

    assert coupon is not None
    assert cart.coupon is not None

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
