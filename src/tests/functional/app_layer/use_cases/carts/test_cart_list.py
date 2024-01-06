from datetime import datetime, timedelta

import pytest
from _pytest.fixtures import SubRequest

from app.app_layer.interfaces.auth_system.exceptions import OperationForbiddenError
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.use_cases.carts.cart_list import CartListUseCase
from app.app_layer.use_cases.carts.dto import CartListInputDTO
from app.domain.cart_config.entities import CartConfig
from app.domain.carts.dto import CartDTO
from app.domain.carts.entities import Cart
from app.domain.carts.value_objects import CartStatusEnum
from tests.environment.unit_of_work import TestUow
from tests.utils import fake

pytestmark = [pytest.mark.usefixtures("carts")]


@pytest.fixture()
def page_size() -> int:
    return fake.numeric.integer_number(start=2, end=5)


@pytest.fixture()
async def carts(uow: TestUow, cart_config: CartConfig, page_size: int) -> list[Cart]:
    carts_qty = page_size * 3
    created_at = datetime.now() - timedelta(days=1)

    carts = [
        Cart(
            data=CartDTO(
                created_at=created_at,
                id=fake.cryptographic.uuid_object(),
                user_id=fake.numeric.integer_number(start=1),
                status=CartStatusEnum.DEACTIVATED,
            ),
            items=[],
            config=cart_config,
        )
        for _ in range(carts_qty)
    ]

    async with uow(autocommit=True):
        await uow.carts.bulk_create(carts=carts)

    return carts


@pytest.fixture()
def use_case(uow: TestUow, auth_system: IAuthSystem) -> CartListUseCase:
    return CartListUseCase(uow=uow, auth_system=auth_system)


@pytest.fixture()
def dto(request: SubRequest, page_size: int) -> CartListInputDTO:
    extra_data = getattr(request, "param", {})

    return CartListInputDTO(
        **{
            "page_size": page_size,
            "created_at": datetime.now(),
            "auth_data": "Bearer admin.1",
            **extra_data,
        },
    )


@pytest.mark.parametrize(
    "dto",
    [
        pytest.param({"created_at": datetime.now()}, id="with created_at"),
        pytest.param({"created_at": None}, id="without created_at"),
    ],
    indirect=True,
)
async def test_ok(
    page_size: int,
    use_case: CartListUseCase,
    dto: CartListInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    result = await use_case.execute(data=dto)
    assert len(result) == page_size


@pytest.mark.parametrize(
    "dto",
    [{"created_at": datetime.now() - timedelta(days=2)}],
    indirect=True,
)
async def test_empty_result(
    page_size: int,
    use_case: CartListUseCase,
    dto: CartListInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    result = await use_case.execute(data=dto)
    assert len(result) == 0


@pytest.mark.parametrize("dto", [{"auth_data": "Bearer customer.1"}], indirect=True)
async def test_forbidden(
    page_size: int,
    use_case: CartListUseCase,
    dto: CartListInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(OperationForbiddenError, match=""):
        await use_case.execute(data=dto)
