from unittest.mock import ANY, AsyncMock

import pytest

from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.use_cases.carts.cart_lock import LockCartUseCase
from app.config import RedisLockConfig
from app.domain.carts.entities import Cart
from app.domain.carts.value_objects import CartStatusEnum
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError
from tests.environment.unit_of_work import TestUow
from tests.utils import fake


@pytest.fixture()
def use_case(
    uow: TestUow,
    distributed_lock_system: IDistributedLockSystem,
) -> LockCartUseCase:
    return LockCartUseCase(uow=uow, distributed_lock_system=distributed_lock_system)


async def test_ok(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: LockCartUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    result = await use_case.execute(cart_id=cart.id)

    async with uow(autocommit=True):
        cart = await uow.carts.retrieve(cart_id=cart.id)

    assert result.status == cart.status == CartStatusEnum.LOCKED

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
    use_case: LockCartUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(AlreadyLockedError, match=""):
        await use_case.execute(cart_id=cart.id)

    async with uow(autocommit=True):
        cart = await uow.carts.retrieve(cart_id=cart.id)

    assert cart.status != CartStatusEnum.LOCKED

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )


async def test_cart_not_found(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: LockCartUseCase,
) -> None:
    cart_id = fake.cryptographic.uuid_object()

    with pytest.raises(CartNotFoundError, match=""):
        await use_case.execute(cart_id=cart_id)

    redis.set.assert_awaited_with(
        f"cart-lock-{cart_id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
