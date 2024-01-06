import pytest
from _pytest.fixtures import SubRequest

from app.app_layer.interfaces.auth_system.exceptions import OperationForbiddenError
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.use_cases.cart_config.dto import CartConfigInputDTO
from app.app_layer.use_cases.cart_config.service import CartConfigService
from app.domain.cart_config.entities import CartConfig
from tests.environment.unit_of_work import TestUow
from tests.utils import fake


@pytest.fixture()
async def cart_config(cart_config: CartConfig, uow: TestUow) -> CartConfig:
    async with uow(autocommit=True):
        await uow.carts.update_config(cart_config=cart_config)

    return cart_config


@pytest.fixture()
def service(uow: TestUow, auth_system: IAuthSystem) -> CartConfigService:
    return CartConfigService(uow=uow, auth_system=auth_system)


@pytest.fixture()
def dto(request: SubRequest) -> CartConfigInputDTO:
    extra_data = getattr(request, "param", {})

    return CartConfigInputDTO(
        **{
            "max_items_qty": fake.numeric.integer_number(start=1),
            "min_cost_for_checkout": fake.numeric.integer_number(start=1),
            "limit_items_by_id": {},
            "hours_since_update_until_abandoned": fake.numeric.integer_number(start=1),
            "max_abandoned_notifications_qty": fake.numeric.integer_number(start=1),
            "abandoned_cart_text": fake.text.word(),
            "auth_data": "Bearer admin.1",
            **extra_data,
        },
    )


async def test_retrieve_ok(service: CartConfigService, cart_config: CartConfig) -> None:
    result = await service.retrieve(auth_data="Bearer admin.1")

    assert result.max_items_qty == cart_config.max_items_qty
    assert result.min_cost_for_checkout == cart_config.min_cost_for_checkout
    assert result.limit_items_by_id == cart_config.limit_items_by_id
    assert (
        result.hours_since_update_until_abandoned
        == cart_config.hours_since_update_until_abandoned
    )
    assert (
        result.max_abandoned_notifications_qty
        == cart_config.max_abandoned_notifications_qty
    )
    assert result.abandoned_cart_text == cart_config.abandoned_cart_text


async def test_retrieve_forbidden(service: CartConfigService) -> None:
    with pytest.raises(OperationForbiddenError, match=""):
        await service.retrieve(auth_data="Bearer customer.1")


@pytest.mark.usefixtures("cart_config")
async def test_update_ok(
    service: CartConfigService, dto: CartConfigInputDTO, uow: TestUow
) -> None:
    result = await service.update(data=dto)

    async with uow(autocommit=True):
        config = await uow.carts.get_config()

    assert result.max_items_qty == config.max_items_qty == dto.max_items_qty
    assert (
        result.min_cost_for_checkout
        == config.min_cost_for_checkout
        == dto.min_cost_for_checkout
    )
    assert result.limit_items_by_id == config.limit_items_by_id == dto.limit_items_by_id
    assert (
        result.hours_since_update_until_abandoned
        == config.hours_since_update_until_abandoned
        == dto.hours_since_update_until_abandoned
    )
    assert (
        result.max_abandoned_notifications_qty
        == config.max_abandoned_notifications_qty
        == dto.max_abandoned_notifications_qty
    )
    assert (
        result.abandoned_cart_text
        == config.abandoned_cart_text
        == dto.abandoned_cart_text
    )


@pytest.mark.parametrize("dto", [{"auth_data": "Bearer customer.1"}], indirect=True)
async def test_update_forbidden(
    service: CartConfigService, dto: CartConfigInputDTO
) -> None:
    with pytest.raises(OperationForbiddenError, match=""):
        await service.update(data=dto)
