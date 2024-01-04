import pytest

from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.use_cases.carts.create_cart import CreateCartUseCase
from app.domain.carts.entities import Cart
from app.domain.carts.value_objects import CartStatusEnum
from app.domain.interfaces.repositories.carts.exceptions import (
    ActiveCartAlreadyExistsError,
)
from tests.environment.unit_of_work import TestUow


@pytest.fixture()
def auth_data() -> str:
    return "Bearer customer.1"


@pytest.fixture()
def use_case(uow: TestUow, auth_system: IAuthSystem) -> CreateCartUseCase:
    return CreateCartUseCase(uow=uow, auth_system=auth_system)


async def test_ok(
    use_case: CreateCartUseCase,
    uow: TestUow,
    auth_data: str,
) -> None:
    result = await use_case.create_by_auth_data(auth_data=auth_data)

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=result.id)

    assert result.created_at == cart.created_at
    assert result.id == cart.id
    assert result.user_id == cart.user_id
    assert result.status == cart.status == CartStatusEnum.OPENED
    assert result.items == cart.items == []
    assert result.items_qty == cart.items_qty == 0
    assert result.cost == cart.cost == 0
    assert result.checkout_enabled is False
    assert cart.checkout_enabled is False
    assert result.coupon is None
    assert cart.coupon is None


@pytest.mark.parametrize("cart", [{"user_id": 1}], indirect=True)
async def test_already_exists(
    use_case: CreateCartUseCase,
    auth_data: str,
    cart: Cart,
) -> None:
    with pytest.raises(ActiveCartAlreadyExistsError, match=""):
        await use_case.create_by_auth_data(auth_data=auth_data)


async def test_invalid_auth_data(use_case: CreateCartUseCase) -> None:
    with pytest.raises(InvalidAuthDataError, match=""):
        await use_case.create_by_auth_data(auth_data="INVALID AUTH DATA")
