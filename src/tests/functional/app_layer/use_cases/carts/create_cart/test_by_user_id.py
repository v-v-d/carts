import pytest
from _pytest.fixtures import SubRequest

from app.app_layer.interfaces.auth_system.exceptions import (
    InvalidAuthDataError,
    OperationForbiddenError,
)
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.use_cases.carts.create_cart import CreateCartUseCase
from app.app_layer.use_cases.carts.dto import CartCreateByUserIdInputDTO
from app.domain.carts.entities import Cart
from app.domain.carts.value_objects import CartStatusEnum
from app.domain.interfaces.repositories.carts.exceptions import (
    ActiveCartAlreadyExistsError,
)
from tests.environment.unit_of_work import TestUow
from tests.utils import fake


@pytest.fixture()
def use_case(uow: TestUow, auth_system: IAuthSystem) -> CreateCartUseCase:
    return CreateCartUseCase(uow=uow, auth_system=auth_system)


@pytest.fixture()
def dto(request: SubRequest) -> CartCreateByUserIdInputDTO:
    extra_data = getattr(request, "param", {})

    return CartCreateByUserIdInputDTO(
        **{
            "user_id": fake.numeric.integer_number(start=1),
            "auth_data": "Bearer admin.1",
            **extra_data,
        },
    )


async def test_ok(
    use_case: CreateCartUseCase,
    dto: CartCreateByUserIdInputDTO,
    uow: TestUow,
) -> None:
    result = await use_case.create_by_user_id(data=dto)

    async with uow(autocommit=True):
        cart = await uow.carts.get_by_id(cart_id=result.id)

    assert result.created_at == cart.created_at
    assert result.id == cart.id
    assert result.user_id == dto.user_id
    assert result.status == cart.status == CartStatusEnum.OPENED
    assert result.items == cart.items == []
    assert result.items_qty == cart.items_qty == 0
    assert result.cost == cart.cost == 0
    assert result.checkout_enabled is False
    assert cart.checkout_enabled is False
    assert result.coupon is None
    assert cart.coupon is None


@pytest.mark.parametrize(
    ("dto", "cart"),
    [({"user_id": 1}, {"user_id": 1})],
    indirect=True,
)
async def test_already_exists(
    use_case: CreateCartUseCase,
    dto: CartCreateByUserIdInputDTO,
    cart: Cart,
) -> None:
    with pytest.raises(ActiveCartAlreadyExistsError, match=""):
        await use_case.create_by_user_id(data=dto)


@pytest.mark.parametrize("dto", [{"auth_data": "INVALID AUTH DATA"}], indirect=True)
async def test_invalid_auth_data(
    use_case: CreateCartUseCase,
    dto: CartCreateByUserIdInputDTO,
) -> None:
    with pytest.raises(InvalidAuthDataError, match=""):
        await use_case.create_by_user_id(data=dto)


@pytest.mark.parametrize("dto", [{"auth_data": "Bearer customer.1"}], indirect=True)
async def test_forbidden(
    use_case: CreateCartUseCase,
    dto: CartCreateByUserIdInputDTO,
) -> None:
    with pytest.raises(OperationForbiddenError, match=""):
        await use_case.create_by_user_id(data=dto)
