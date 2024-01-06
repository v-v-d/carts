from http import HTTPMethod
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest

from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.clients.coupons.client import ICouponsClient
from app.app_layer.interfaces.clients.coupons.exceptions import CouponsClientError
from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.use_cases.carts.cart_apply_coupon import CartApplyCouponUseCase
from app.app_layer.use_cases.carts.dto import CartApplyCouponInputDTO
from app.config import RedisLockConfig
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import NotOwnedByUserError
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError
from app.infra.http.transports.base import (
    HttpRequestInputDTO,
    HttpTransportConfig,
    HttpTransportError,
)
from tests.environment.unit_of_work import TestUow
from tests.utils import fake


@pytest.fixture()
def use_case(
    uow: TestUow,
    coupons_client: ICouponsClient,
    auth_system: IAuthSystem,
    distributed_lock_system: IDistributedLockSystem,
) -> CartApplyCouponUseCase:
    return CartApplyCouponUseCase(
        uow=uow,
        coupons_client=coupons_client,
        auth_system=auth_system,
        distributed_lock_system=distributed_lock_system,
    )


@pytest.fixture()
def dto(cart: Cart, auth_data: str) -> CartApplyCouponInputDTO:
    return CartApplyCouponInputDTO(
        cart_id=cart.id,
        coupon_name=fake.text.word(),
        auth_data=auth_data,
    )


@pytest.mark.parametrize(
    ("cart", "http_response"),
    [
        (
            {"user_id": 1},
            {
                "returns": {
                    "min_cart_cost": fake.numeric.integer_number(start=1),
                    "discount_abs": fake.numeric.integer_number(start=1),
                },
            },
        ),
    ],
    indirect=True,
)
async def test_ok(
    http_response: AsyncMock,
    http_session: MagicMock,
    client_base_url: str,
    http_config: HttpTransportConfig,
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartApplyCouponUseCase,
    dto: CartApplyCouponInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    result = await use_case.execute(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.retrieve(cart_id=cart.id)

    assert cart.coupon.cart == cart
    assert result.coupon.coupon_id == cart.coupon.coupon_id == dto.coupon_name
    assert (
        result.coupon.min_cart_cost
        == cart.coupon.min_cart_cost
        == http_response.json.return_value["min_cart_cost"]
    )
    assert (
        result.coupon.discount_abs
        == cart.coupon.discount_abs
        == http_response.json.return_value["discount_abs"]
    )
    assert (
        result.coupon.cart_cost
        == cart.coupon.cart_cost
        == cart.cost - cart.coupon.discount_abs
    )
    assert (
        result.coupon.applied
        == cart.coupon.applied
        == (cart.cost >= cart.coupon.min_cart_cost)
    )

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_called_once_with(
        method=HTTPMethod.GET,
        url=f"{client_base_url}coupons",
        headers={"Accept": "application/json"},
        params={"name": dto.coupon_name},
        data=None,
        json=None,
        trace_request_ctx=SimpleNamespace(
            data=HttpRequestInputDTO(
                method=HTTPMethod.GET,
                url=f"{client_base_url}coupons",
                headers={"Accept": "application/json"},
                params={"name": dto.coupon_name},
                body=None,
            ),
            integration_name=http_config.integration_name,
        ),
    )


@pytest.mark.parametrize(
    "http_response",
    [
        {
            "returns": {
                "min_cart_cost": fake.numeric.integer_number(start=1),
                "discount_abs": fake.numeric.integer_number(start=1),
            },
        },
    ],
    indirect=True,
)
async def test_apply_by_admin(
    http_response: AsyncMock,
    http_session: MagicMock,
    client_base_url: str,
    http_config: HttpTransportConfig,
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartApplyCouponUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    dto = CartApplyCouponInputDTO(
        cart_id=cart.id,
        coupon_name=fake.text.word(),
        auth_data="Bearer admin.1",
    )

    result = await use_case.execute(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.retrieve(cart_id=cart.id)

    assert cart.coupon.cart == cart
    assert result.coupon.coupon_id == cart.coupon.coupon_id == dto.coupon_name
    assert (
        result.coupon.min_cart_cost
        == cart.coupon.min_cart_cost
        == http_response.json.return_value["min_cart_cost"]
    )
    assert (
        result.coupon.discount_abs
        == cart.coupon.discount_abs
        == http_response.json.return_value["discount_abs"]
    )
    assert (
        result.coupon.cart_cost
        == cart.coupon.cart_cost
        == cart.cost - cart.coupon.discount_abs
    )
    assert (
        result.coupon.applied
        == cart.coupon.applied
        == (cart.cost >= cart.coupon.min_cart_cost)
    )

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_called_once_with(
        method=HTTPMethod.GET,
        url=f"{client_base_url}coupons",
        headers={"Accept": "application/json"},
        params={"name": dto.coupon_name},
        data=None,
        json=None,
        trace_request_ctx=SimpleNamespace(
            data=HttpRequestInputDTO(
                method=HTTPMethod.GET,
                url=f"{client_base_url}coupons",
                headers={"Accept": "application/json"},
                params={"name": dto.coupon_name},
                body=None,
            ),
            integration_name=http_config.integration_name,
        ),
    )


@pytest.mark.parametrize("redis", [{"returns": False}], indirect=True)
async def test_cart_already_locked_for_updates(
    http_session: MagicMock,
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartApplyCouponUseCase,
    dto: CartApplyCouponInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(AlreadyLockedError, match=""):
        await use_case.execute(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.retrieve(cart_id=cart.id)

    assert cart.coupon is None

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_not_called()


async def test_invalid_auth_data(
    http_session: MagicMock,
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartApplyCouponUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(InvalidAuthDataError, match=""):
        await use_case.execute(
            data=CartApplyCouponInputDTO(
                cart_id=cart.id,
                coupon_name=fake.text.word(),
                auth_data="INVALID AUTH DATA",
            ),
        )

    async with uow(autocommit=True):
        cart = await uow.carts.retrieve(cart_id=cart.id)

    assert cart.coupon is None

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_not_called()


async def test_cart_not_found(
    http_session: MagicMock,
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartApplyCouponUseCase,
) -> None:
    cart_id = fake.cryptographic.uuid_object()

    with pytest.raises(CartNotFoundError, match=""):
        await use_case.execute(
            data=CartApplyCouponInputDTO(
                cart_id=cart_id,
                coupon_name=fake.text.word(),
                auth_data="Bearer customer.1",
            ),
        )

    redis.set.assert_awaited_with(
        f"cart-lock-{cart_id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_not_called()


async def test_not_owned_by_current_user(
    http_session: MagicMock,
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartApplyCouponUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(NotOwnedByUserError, match=""):
        await use_case.execute(
            data=CartApplyCouponInputDTO(
                cart_id=cart.id,
                coupon_name=fake.text.word(),
                auth_data="Bearer customer.2",
            ),
        )

    async with uow(autocommit=True):
        cart = await uow.carts.retrieve(cart_id=cart.id)

    assert cart.coupon is None

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_not_called()


@pytest.mark.parametrize(
    ("cart", "http_response"),
    [
        (
            {"user_id": 1},
            {"raises": HttpTransportError(message="test", code=123)},
        ),
    ],
    indirect=True,
)
async def test_failed_coupons_client(
    http_response: AsyncMock,
    http_session: MagicMock,
    http_config: HttpTransportConfig,
    client_base_url: str,
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: CartApplyCouponUseCase,
    dto: CartApplyCouponInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(CouponsClientError, match="123 - test"):
        await use_case.execute(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.retrieve(cart_id=cart.id)

    assert cart.coupon is None

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_called_once_with(
        method=HTTPMethod.GET,
        url=f"{client_base_url}coupons",
        headers={"Accept": "application/json"},
        params={"name": dto.coupon_name},
        data=None,
        json=None,
        trace_request_ctx=SimpleNamespace(
            data=HttpRequestInputDTO(
                method=HTTPMethod.GET,
                url=f"{client_base_url}coupons",
                headers={"Accept": "application/json"},
                params={"name": dto.coupon_name},
                body=None,
            ),
            integration_name=http_config.integration_name,
        ),
    )
