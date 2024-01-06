from datetime import datetime
from decimal import Decimal
from http import HTTPMethod
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest

from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.clients.products.client import IProductsClient
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.use_cases.cart_items.add_item import AddCartItemUseCase
from app.app_layer.use_cases.cart_items.dto import AddItemToCartInputDTO
from app.config import RedisLockConfig
from app.domain.cart_config.entities import CartConfig
from app.domain.cart_items.entities import CartItem
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

CART_ITEM_ID = fake.numeric.integer_number(start=1)
FROZEN_TIME = datetime.now()

pytestmark = [pytest.mark.freeze_time(FROZEN_TIME)]


@pytest.fixture()
def use_case(
    uow: TestUow,
    products_client: IProductsClient,
    auth_system: IAuthSystem,
    distributed_lock_system: IDistributedLockSystem,
) -> AddCartItemUseCase:
    return AddCartItemUseCase(
        uow=uow,
        products_client=products_client,
        auth_system=auth_system,
        distributed_lock_system=distributed_lock_system,
    )


@pytest.fixture()
async def cart_config(uow: TestUow) -> CartConfig:
    async with uow(autocommit=True):
        return await uow.carts.get_config()


@pytest.fixture()
async def cart(uow: TestUow, cart_config: CartConfig) -> Cart:
    cart = Cart.create(user_id=1, config=cart_config)

    async with uow(autocommit=True):
        await uow.carts.create(cart=cart)

    return cart


@pytest.fixture()
def auth_data() -> str:
    return "Bearer customer.1"


@pytest.fixture()
def dto(cart: Cart, cart_config: CartConfig, auth_data: str) -> AddItemToCartInputDTO:
    return AddItemToCartInputDTO(
        id=CART_ITEM_ID,
        qty=fake.numeric.integer_number(start=1, end=cart_config.max_items_qty - 1),
        auth_data=auth_data,
        cart_id=cart.id,
    )


@pytest.mark.parametrize(
    "http_response",
    [
        {
            "returns": {
                "id": fake.numeric.integer_number(start=1),
                "title": fake.text.word(),
                "price": fake.numeric.integer_number(start=1),
                "description": fake.text.word(),
                "category": fake.text.word(),
                "image": fake.internet.stock_image_url(),
                "rating": {
                    "rate": fake.numeric.float_number(start=1, precision=2),
                    "count": fake.numeric.integer_number(start=1),
                },
            },
        },
    ],
    indirect=True,
)
async def test_new_item_ok(
    http_response: AsyncMock,
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    http_session: MagicMock,
    http_config: HttpTransportConfig,
    client_base_url: str,
    use_case: AddCartItemUseCase,
    dto: AddItemToCartInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    result = await use_case.execute(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.retrieve(cart_id=cart.id)

    assert len(result.items) == len(cart.items) == 1
    assert result.items[0].id == cart.items[0].id == dto.id
    assert (
        result.items[0].name
        == cart.items[0].name
        == http_response.json.return_value["title"]
    )
    assert result.items[0].qty == cart.items[0].qty == dto.qty
    assert (
        result.items[0].price
        == cart.items[0].price
        == Decimal(http_response.json.return_value["price"])
    )
    assert (
        result.items[0].cost
        == cart.items[0].cost
        == Decimal(http_response.json.return_value["price"] * dto.qty)
    )
    assert result.items[0].is_weight == cart.items[0].is_weight is False
    assert (
        result.cost
        == cart.cost
        == Decimal(http_response.json.return_value["price"]) * dto.qty
    )

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_called_once_with(
        method=HTTPMethod.GET,
        url=f"{client_base_url}products/{dto.id}",
        headers=None,
        params=None,
        data=None,
        json=None,
        trace_request_ctx=SimpleNamespace(
            data=HttpRequestInputDTO(
                method=HTTPMethod.GET,
                url=f"{client_base_url}products/{dto.id}",
                headers=None,
                params=None,
                body=None,
            ),
            integration_name=http_config.integration_name,
        ),
    )


@pytest.mark.parametrize("cart_item", [{"id": CART_ITEM_ID, "qty": 1}], indirect=True)
async def test_existing_item_ok(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    http_session: MagicMock,
    uow: TestUow,
    use_case: AddCartItemUseCase,
    dto: AddItemToCartInputDTO,
    cart: Cart,
    cart_item: CartItem,
) -> None:
    cart.add_new_item(item=cart_item)
    async with uow(autocommit=True):
        await uow.items.add_item(item=cart_item)

    result = await use_case.execute(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.retrieve(cart_id=cart.id)

    assert len(result.items) == len(cart.items) == 1
    assert result.items[0].id == cart.items[0].id == dto.id
    assert result.items[0].name == cart.items[0].name == cart_item.name
    assert result.items[0].qty == cart.items[0].qty == cart_item.qty + dto.qty
    assert result.items[0].price == cart.items[0].price == cart_item.price
    assert (
        result.items[0].cost
        == cart.items[0].cost
        == cart_item.price * (cart_item.qty + dto.qty)
    )
    assert result.items[0].is_weight == cart.items[0].is_weight is cart_item.is_weight
    assert result.cost == cart.cost == cart_item.price * (cart_item.qty + dto.qty)

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_not_called()


@pytest.mark.parametrize("cart_item", [{"id": CART_ITEM_ID, "qty": 1}], indirect=True)
async def test_increase_item_qty_by_admin(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    http_session: MagicMock,
    uow: TestUow,
    use_case: AddCartItemUseCase,
    cart: Cart,
    cart_config: CartConfig,
    cart_item: CartItem,
) -> None:
    cart.add_new_item(item=cart_item)
    async with uow(autocommit=True):
        await uow.items.add_item(item=cart_item)

    dto = AddItemToCartInputDTO(
        id=CART_ITEM_ID,
        qty=fake.numeric.integer_number(start=1, end=cart_config.max_items_qty - 1),
        auth_data="Bearer admin.1",
        cart_id=cart.id,
    )

    result = await use_case.execute(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.retrieve(cart_id=cart.id)

    assert len(result.items) == len(cart.items) == 1
    assert result.items[0].id == cart.items[0].id == dto.id
    assert result.items[0].name == cart.items[0].name == cart_item.name
    assert result.items[0].qty == cart.items[0].qty == cart_item.qty + dto.qty
    assert result.items[0].price == cart.items[0].price == cart_item.price
    assert (
        result.items[0].cost
        == cart.items[0].cost
        == cart_item.price * (cart_item.qty + dto.qty)
    )
    assert result.items[0].is_weight == cart.items[0].is_weight is cart_item.is_weight
    assert result.cost == cart.cost == cart_item.price * (cart_item.qty + dto.qty)

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_not_called()


@pytest.mark.parametrize("redis", [{"returns": False}], indirect=True)
async def test_cart_already_locked_for_updates(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    http_session: MagicMock,
    use_case: AddCartItemUseCase,
    dto: AddItemToCartInputDTO,
    cart: Cart,
) -> None:
    with pytest.raises(AlreadyLockedError, match=""):
        await use_case.execute(data=dto)

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_not_called()


async def test_invalid_auth_data(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    http_session: MagicMock,
    use_case: AddCartItemUseCase,
    cart: Cart,
) -> None:
    with pytest.raises(InvalidAuthDataError, match=""):
        await use_case.execute(
            data=AddItemToCartInputDTO(
                id=fake.numeric.integer_number(start=1),
                qty=fake.numeric.integer_number(start=1),
                auth_data="INVALID AUTH DATA",
                cart_id=cart.id,
            ),
        )

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_not_called()


async def test_cart_not_found(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    http_session: MagicMock,
    use_case: AddCartItemUseCase,
) -> None:
    cart_id = fake.cryptographic.uuid_object()

    with pytest.raises(CartNotFoundError, match=""):
        await use_case.execute(
            data=AddItemToCartInputDTO(
                id=fake.numeric.integer_number(start=1),
                qty=fake.numeric.integer_number(start=1),
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
    http_session.request.assert_not_called()


async def test_not_owned_by_current_user(
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    http_session: MagicMock,
    use_case: AddCartItemUseCase,
    cart: Cart,
) -> None:
    with pytest.raises(NotOwnedByUserError, match=""):
        await use_case.execute(
            data=AddItemToCartInputDTO(
                id=fake.numeric.integer_number(start=1),
                qty=fake.numeric.integer_number(start=1),
                auth_data="Bearer customer.2",
                cart_id=cart.id,
            ),
        )

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_not_called()


@pytest.mark.parametrize(
    "http_response",
    [{"raises": HttpTransportError(message="test", code=123)}],
    indirect=True,
)
async def test_failed_products_client(
    http_response: AsyncMock,
    http_session: MagicMock,
    http_config: HttpTransportConfig,
    client_base_url: str,
    redis: AsyncMock,
    redis_lock_config: RedisLockConfig,
    use_case: AddCartItemUseCase,
    dto: AddItemToCartInputDTO,
    cart: Cart,
) -> None:
    with pytest.raises(ProductsClientError, match="123 - test"):
        await use_case.execute(data=dto)

    redis.set.assert_awaited_with(
        f"cart-lock-{cart.id}",
        ANY,
        nx=True,
        px=redis_lock_config.ttl_sec * 1000,
    )
    http_session.request.assert_called_once_with(
        method=HTTPMethod.GET,
        url=f"{client_base_url}products/{dto.id}",
        headers=None,
        params=None,
        data=None,
        json=None,
        trace_request_ctx=SimpleNamespace(
            data=HttpRequestInputDTO(
                method=HTTPMethod.GET,
                url=f"{client_base_url}products/{dto.id}",
                headers=None,
                params=None,
                body=None,
            ),
            integration_name=http_config.integration_name,
        ),
    )
