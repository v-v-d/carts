from unittest.mock import ANY, AsyncMock

import pytest

from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.use_cases.cart_items.dto import ClearCartInputDTO
from app.app_layer.use_cases.carts.clear_cart import ClearCartUseCase
from app.config import RedisLockConfig
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import NotOwnedByUserError
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError
from tests.environment.unit_of_work import TestUow
from tests.utils import fake


@pytest.fixture()
def use_case(
    uow: TestUow,
    auth_system: IAuthSystem,
    distributed_lock_system: IDistributedLockSystem,
) -> ClearCartUseCase:
    return ClearCartUseCase(
        uow=uow,
        auth_system=auth_system,
        distributed_lock_system=distributed_lock_system,
    )


@pytest.fixture()
def dto(cart: Cart, cart_item: CartItem, auth_data: str) -> ClearCartInputDTO:
    return ClearCartInputDTO(auth_data=auth_data, cart_id=cart.id)


@pytest.mark.parametrize("cart", [{"user_id": 1}], indirect=True)
async def test_ok(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: ClearCartUseCase,
    dto: ClearCartInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    result = await use_case.execute(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=cart.id)

    assert len(result.items) == len(cart.items) == 0

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )


async def test_clear_by_admin(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: ClearCartUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    result = await use_case.execute(
        data=ClearCartInputDTO(
            auth_data="Bearer admin.1",
            cart_id=cart.id,
        )
    )

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=cart.id)

    assert len(result.items) == len(cart.items) == 0

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
    use_case: ClearCartUseCase,
    dto: ClearCartInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(AlreadyLockedError, match=""):
        await use_case.execute(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=cart.id)

    assert len(cart.items) > 0

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )


async def test_invalid_auth_data(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: ClearCartUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(InvalidAuthDataError, match=""):
        await use_case.execute(
            data=ClearCartInputDTO(
                auth_data="INVALID AUTH DATA",
                cart_id=cart.id,
            ),
        )

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=cart.id)

    assert len(cart.items) > 0

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )


async def test_cart_not_found(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: ClearCartUseCase,
) -> None:
    cart_id = fake.cryptographic.uuid_object()

    with pytest.raises(CartNotFoundError, match=""):
        await use_case.execute(
            data=ClearCartInputDTO(
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
    use_case: ClearCartUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(NotOwnedByUserError, match=""):
        await use_case.execute(
            data=ClearCartInputDTO(
                auth_data="Bearer customer.2",
                cart_id=cart.id,
            ),
        )

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=cart.id)

    assert len(cart.items) > 0

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
