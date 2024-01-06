from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from _pytest.fixtures import SubRequest
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.clients.coupons.exceptions import CouponsClientError
from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.use_cases.carts.cart_apply_coupon import CartApplyCouponUseCase
from app.app_layer.use_cases.carts.dto import CartCouponOutputDTO, CartOutputDTO
from app.domain.carts.exceptions import (
    CouponAlreadyAppliedError,
    NotOwnedByUserError,
    OperationForbiddenError,
)
from app.domain.carts.value_objects import CartStatusEnum
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError
from tests.utils import fake


@pytest.fixture()
def url_path(cart_id: UUID) -> str:
    return f"api/v1/carts/{cart_id}/apply-coupon"


@pytest.fixture()
def use_case(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=CartApplyCouponUseCase)

    if "returns" in request.param:
        mock.execute.return_value = request.param["returns"]
    elif "raises" in request.param:
        mock.execute.side_effect = request.param["raises"]

    return mock


@pytest.fixture()
def application(application: FastAPI, use_case: AsyncMock) -> FastAPI:
    with application.container.cart_apply_coupon_use_case.override(use_case):
        yield application


@pytest.mark.parametrize(
    "use_case",
    [
        {
            "returns": CartOutputDTO(
                created_at=fake.datetime.datetime(),
                id=fake.cryptographic.uuid_object(),
                user_id=fake.numeric.integer_number(start=1),
                status=CartStatusEnum.OPENED,
                items=[],
                items_qty=0,
                cost=0,
                checkout_enabled=False,
                coupon=CartCouponOutputDTO(
                    coupon_id=fake.text.word(),
                    min_cart_cost=fake.numeric.integer_number(start=1),
                    discount_abs=fake.numeric.integer_number(start=1),
                    cart_cost=fake.numeric.integer_number(start=1),
                    applied=fake.random.choice([True, False]),
                ),
            ),
        }
    ],
    indirect=True,
)
async def test_ok(http_client: AsyncClient, use_case: AsyncMock, url_path: str) -> None:
    response = await http_client.post(
        url=url_path,
        data={"coupon_name": fake.text.word()},
    )

    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json() == {
        "id": str(use_case.execute.return_value.id),
        "user_id": use_case.execute.return_value.user_id,
        "status": use_case.execute.return_value.status.value,
        "items": use_case.execute.return_value.items,
        "items_quantity": float(use_case.execute.return_value.items_qty),
        "cost": float(use_case.execute.return_value.cost),
        "checkout_enabled": use_case.execute.return_value.checkout_enabled,
        "coupon": {
            "coupon_id": use_case.execute.return_value.coupon.coupon_id,
            "discount_abs": float(use_case.execute.return_value.coupon.discount_abs),
            "cart_cost": float(use_case.execute.return_value.coupon.cart_cost),
            "applied": use_case.execute.return_value.coupon.applied,
        },
    }


@pytest.mark.parametrize(
    ("use_case", "expected_code", "expected_error"),
    [
        pytest.param(
            {"raises": AlreadyLockedError},
            HTTPStatus.BAD_REQUEST,
            {
                "detail": {
                    "code": 5000,
                    "message": "The action couldn't be processed. The cart is already being processed.",
                },
            },
            id="AlreadyLockedError",
        ),
        pytest.param(
            {"raises": InvalidAuthDataError},
            HTTPStatus.UNAUTHORIZED,
            {"detail": {"code": 1000, "message": "Authorization failed."}},
            id="UNAUTHORIZED",
        ),
        pytest.param(
            {"raises": CartNotFoundError},
            HTTPStatus.BAD_REQUEST,
            {"detail": {"code": 2000, "message": "Cart not found."}},
            id="CART_NOT_FOUND",
        ),
        pytest.param(
            {"raises": NotOwnedByUserError},
            HTTPStatus.BAD_REQUEST,
            {"detail": {"code": 2000, "message": "Cart not found."}},
            id="FORBIDDEN",
        ),
        pytest.param(
            {"raises": CouponAlreadyAppliedError},
            HTTPStatus.BAD_REQUEST,
            {
                "detail": {
                    "code": 4000,
                    "message": (
                        "Coupon has already been applied. You need to delete the existing coupon "
                        "before applying a new one."
                    ),
                }
            },
            id="ALREADY_APPLIED",
        ),
        pytest.param(
            {"raises": CouponsClientError},
            HTTPStatus.BAD_REQUEST,
            {
                "detail": {
                    "code": 4001,
                    "message": "Failed to apply the coupon. Please try applying it again.",
                },
            },
            id="CLIENT_ERROR",
        ),
        pytest.param(
            {"raises": OperationForbiddenError},
            HTTPStatus.BAD_REQUEST,
            {"detail": {"code": 2003, "message": "The cart can't be modified."}},
            id="OPERATION_FORBIDDEN",
        ),
    ],
    indirect=["use_case"],
)
async def test_failed(
    http_client: AsyncClient,
    use_case: AsyncMock,
    url_path: str,
    expected_code: int,
    expected_error: dict[str, Any],
) -> None:
    response = await http_client.post(
        url=url_path,
        data={"coupon_name": fake.text.word()},
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_error
