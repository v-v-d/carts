from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock

import pytest
from _pytest.fixtures import SubRequest
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.use_cases.carts.create_cart import CreateCartUseCase
from app.app_layer.use_cases.carts.dto import CartOutputDTO
from app.domain.carts.value_objects import CartStatusEnum
from app.domain.interfaces.repositories.carts.exceptions import (
    ActiveCartAlreadyExistsError,
)
from tests.utils import fake


@pytest.fixture()
def url_path() -> str:
    return "api/v1/carts"


@pytest.fixture()
def use_case(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=CreateCartUseCase)

    if "returns" in request.param:
        mock.create_by_auth_data.return_value = request.param["returns"]
    elif "raises" in request.param:
        mock.create_by_auth_data.side_effect = request.param["raises"]

    return mock


@pytest.fixture()
def application(application: FastAPI, use_case: AsyncMock) -> FastAPI:
    with application.container.create_cart_use_case.override(use_case):
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
                coupon=None,
            ),
        }
    ],
    indirect=True,
)
async def test_ok(http_client: AsyncClient, use_case: AsyncMock, url_path: str) -> None:
    response = await http_client.post(url=url_path)

    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json() == {
        "id": str(use_case.create_by_auth_data.return_value.id),
        "user_id": use_case.create_by_auth_data.return_value.user_id,
        "status": use_case.create_by_auth_data.return_value.status.value,
        "items": use_case.create_by_auth_data.return_value.items,
        "items_quantity": float(use_case.create_by_auth_data.return_value.items_qty),
        "cost": float(use_case.create_by_auth_data.return_value.cost),
        "checkout_enabled": use_case.create_by_auth_data.return_value.checkout_enabled,
        "coupon": use_case.create_by_auth_data.return_value.coupon,
    }


@pytest.mark.parametrize(
    ("use_case", "expected_code", "expected_error"),
    [
        pytest.param(
            {"raises": InvalidAuthDataError},
            HTTPStatus.UNAUTHORIZED,
            {"detail": {"code": 1000, "message": "Authorization failed."}},
            id="UNAUTHORIZED",
        ),
        pytest.param(
            {"raises": ActiveCartAlreadyExistsError},
            HTTPStatus.BAD_REQUEST,
            {"detail": {"code": 2001, "message": "Active cart already exists."}},
            id="ACTIVE_CART_ALREADY_EXISTS",
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
    response = await http_client.post(url=url_path)

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_error
