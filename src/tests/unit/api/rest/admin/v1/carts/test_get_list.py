from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock

import pytest
from _pytest.fixtures import SubRequest
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app.app_layer.interfaces.auth_system.exceptions import (
    InvalidAuthDataError,
    OperationForbiddenError,
)
from app.app_layer.use_cases.carts.cart_list import CartListUseCase
from app.app_layer.use_cases.carts.dto import CartOutputDTO
from app.domain.carts.value_objects import CartStatusEnum
from tests.utils import fake


@pytest.fixture()
def page_size() -> int:
    return fake.numeric.integer_number(start=1)


@pytest.fixture()
def url_path(page_size: int) -> str:
    return f"api/admin/v1/carts?page_size={page_size}"


@pytest.fixture()
def use_case(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=CartListUseCase)

    if "returns" in request.param:
        mock.execute.return_value = request.param["returns"]
    elif "raises" in request.param:
        mock.execute.side_effect = request.param["raises"]

    return mock


@pytest.fixture()
def application(application: FastAPI, use_case: AsyncMock) -> FastAPI:
    with application.container.cart_list_use_case.override(use_case):
        yield application


@pytest.mark.parametrize(
    "use_case",
    [
        {
            "returns": [
                CartOutputDTO(
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
            ]
        }
    ],
    indirect=True,
)
async def test_ok(
    http_client: AsyncClient, use_case: AsyncMock, url_path: str, page_size: int
) -> None:
    response = await http_client.get(url=url_path)

    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json() == {
        "items": [
            {
                "created_at": use_case.execute.return_value[0].created_at.isoformat(),
                "id": str(use_case.execute.return_value[0].id),
                "user_id": use_case.execute.return_value[0].user_id,
                "status": use_case.execute.return_value[0].status.value,
                "items": use_case.execute.return_value[0].items,
                "items_qty": float(use_case.execute.return_value[0].items_qty),
                "cost": float(use_case.execute.return_value[0].cost),
                "checkout_enabled": use_case.execute.return_value[0].checkout_enabled,
                "coupon": use_case.execute.return_value[0].coupon,
            },
        ],
        "page_size": page_size,
        "next_page": use_case.execute.return_value[0].created_at.isoformat(),
    }


@pytest.mark.parametrize("use_case", [{"returns": []}], indirect=True)
async def test_empty_result(
    http_client: AsyncClient, use_case: AsyncMock, url_path: str, page_size: int
) -> None:
    response = await http_client.get(url=url_path)

    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json() == {
        "items": [],
        "page_size": page_size,
        "next_page": None,
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
            {"raises": OperationForbiddenError},
            HTTPStatus.BAD_REQUEST,
            {"detail": {"code": 1001, "message": "Forbidden."}},
            id="FORBIDDEN",
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
    response = await http_client.get(url=url_path)

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_error
