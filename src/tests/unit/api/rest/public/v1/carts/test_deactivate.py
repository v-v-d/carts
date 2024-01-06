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
from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.use_cases.carts.cart_delete import CartDeleteUseCase
from app.domain.carts.exceptions import ChangeStatusError, NotOwnedByUserError
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError


@pytest.fixture()
def url_path(cart_id: UUID) -> str:
    return f"api/v1/carts/{cart_id}/deactivate"


@pytest.fixture()
def use_case(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=CartDeleteUseCase)

    if "returns" in request.param:
        mock.execute.return_value = request.param["returns"]
    elif "raises" in request.param:
        mock.execute.side_effect = request.param["raises"]

    return mock


@pytest.fixture()
def application(application: FastAPI, use_case: AsyncMock) -> FastAPI:
    with application.container.cart_delete_use_case.override(use_case):
        yield application


@pytest.mark.parametrize("use_case", [{"returns": None}], indirect=True)
async def test_ok(http_client: AsyncClient, use_case: AsyncMock, url_path: str) -> None:
    response = await http_client.post(url=url_path)
    assert response.status_code == HTTPStatus.NO_CONTENT, response.text


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
            {"raises": ChangeStatusError},
            HTTPStatus.BAD_REQUEST,
            {"detail": {"code": 2002, "message": "The cart can't be deactivated."}},
            id="CHANGE_STATUS_ERROR",
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
