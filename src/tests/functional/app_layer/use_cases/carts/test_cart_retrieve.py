import pytest

from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.use_cases.carts.cart_retrieve import CartRetrieveUseCase
from app.app_layer.use_cases.carts.dto import CartRetrieveInputDTO, ItemOutputDTO
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import NotOwnedByUserError
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError
from tests.environment.unit_of_work import TestUow
from tests.utils import fake


@pytest.fixture()
def use_case(uow: TestUow, auth_system: IAuthSystem) -> CartRetrieveUseCase:
    return CartRetrieveUseCase(uow=uow, auth_system=auth_system)


@pytest.fixture()
def dto(cart: Cart, cart_item: CartItem, auth_data: str) -> CartRetrieveInputDTO:
    return CartRetrieveInputDTO(auth_data=auth_data, cart_id=cart.id)


@pytest.mark.parametrize("cart", [{"user_id": 1}], indirect=True)
async def test_ok(
    use_case: CartRetrieveUseCase,
    dto: CartRetrieveInputDTO,
    cart: Cart,
    uow: TestUow,
) -> None:
    result = await use_case.execute(data=dto)

    assert result.created_at == cart.created_at
    assert result.id == cart.id
    assert result.user_id == cart.user_id
    assert result.status == cart.status
    assert len(result.items) == len(cart.items)

    cart_items_by_id = {item.id: item for item in cart.items}

    for item in result.items:
        assert item == ItemOutputDTO.model_validate(cart_items_by_id[item.id])

    assert result.items_qty == cart.items_qty
    assert result.cost == cart.cost
    assert result.checkout_enabled == cart.checkout_enabled
    assert result.coupon == cart.coupon


async def test_retrieve_by_admin(
    use_case: CartRetrieveUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    result = await use_case.execute(
        data=CartRetrieveInputDTO(
            auth_data="Bearer admin.1",
            cart_id=cart.id,
        )
    )

    assert result.created_at == cart.created_at
    assert result.id == cart.id
    assert result.user_id == cart.user_id
    assert result.status == cart.status
    assert len(result.items) == len(cart.items)

    cart_items_by_id = {item.id: item for item in cart.items}

    for item in result.items:
        assert item == ItemOutputDTO.model_validate(cart_items_by_id[item.id])

    assert result.items_qty == cart.items_qty
    assert result.cost == cart.cost
    assert result.checkout_enabled == cart.checkout_enabled
    assert result.coupon == cart.coupon


async def test_invalid_auth_data(
    use_case: CartRetrieveUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(InvalidAuthDataError, match=""):
        await use_case.execute(
            data=CartRetrieveInputDTO(
                auth_data="INVALID AUTH DATA",
                cart_id=cart.id,
            ),
        )


async def test_cart_not_found(use_case: CartRetrieveUseCase) -> None:
    cart_id = fake.cryptographic.uuid_object()

    with pytest.raises(CartNotFoundError, match=""):
        await use_case.execute(
            data=CartRetrieveInputDTO(
                auth_data="Bearer customer.1",
                cart_id=cart_id,
            ),
        )


async def test_not_owned_by_current_user(
    use_case: CartRetrieveUseCase,
    cart: Cart,
    uow: TestUow,
) -> None:
    with pytest.raises(NotOwnedByUserError, match=""):
        await use_case.execute(
            data=CartRetrieveInputDTO(
                auth_data="Bearer customer.2",
                cart_id=cart.id,
            ),
        )
