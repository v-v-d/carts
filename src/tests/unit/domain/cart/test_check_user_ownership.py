import pytest

from app.domain.carts.entities import Cart
from app.domain.carts.exceptions import NotOwnedByUserError


@pytest.mark.parametrize("cart", [{"user_id": 1}], indirect=True)
def test_ok(cart: Cart) -> None:
    cart.check_user_ownership(user_id=1)


@pytest.mark.parametrize("cart", [{"user_id": 2}], indirect=True)
def test_failed(cart: Cart) -> None:
    with pytest.raises(NotOwnedByUserError, match=""):
        cart.check_user_ownership(user_id=1)
