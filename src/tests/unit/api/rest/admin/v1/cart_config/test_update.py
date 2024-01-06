from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock

import pytest
from _pytest.fixtures import SubRequest
from fastapi import FastAPI
from httpx import AsyncClient
from pytest_mock import MockerFixture

from app.app_layer.interfaces.auth_system.exceptions import OperationForbiddenError
from app.app_layer.use_cases.cart_config.dto import CartConfigOutputDTO
from app.app_layer.use_cases.cart_config.service import CartConfigService
from tests.utils import fake


@pytest.fixture()
def url_path() -> str:
    return "api/admin/v1/cart_config"


@pytest.fixture()
def use_case(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=CartConfigService)

    if "returns" in request.param:
        mock.update.return_value = request.param["returns"]
    elif "raises" in request.param:
        mock.update.side_effect = request.param["raises"]

    return mock


@pytest.fixture()
def application(application: FastAPI, use_case: AsyncMock) -> FastAPI:
    with application.container.cart_config_service.override(use_case):
        yield application


@pytest.mark.parametrize(
    "use_case",
    [
        {
            "returns": CartConfigOutputDTO(
                max_items_qty=fake.numeric.integer_number(start=1),
                min_cost_for_checkout=fake.numeric.integer_number(start=1),
                limit_items_by_id={},
                hours_since_update_until_abandoned=fake.numeric.integer_number(start=1),
                max_abandoned_notifications_qty=fake.numeric.integer_number(start=1),
                abandoned_cart_text=fake.text.word(),
            ),
        }
    ],
    indirect=True,
)
async def test_ok(http_client: AsyncClient, use_case: AsyncMock, url_path: str) -> None:
    response = await http_client.put(
        url=url_path,
        json={
            "max_items_qty": fake.numeric.integer_number(start=1),
            "min_cost_for_checkout": fake.numeric.integer_number(start=1),
            "limit_items_by_id": {"1": 3, "3": 6},
            "hours_since_update_until_abandoned": fake.numeric.integer_number(start=1),
            "max_abandoned_notifications_qty": fake.numeric.integer_number(start=1),
            "abandoned_cart_text": fake.text.word(),
        },
    )

    assert response.status_code == HTTPStatus.OK, response.text
    assert response.json() == {
        "max_items_qty": use_case.update.return_value.max_items_qty,
        "min_cost_for_checkout": int(use_case.update.return_value.min_cost_for_checkout),
        "limit_items_by_id": use_case.update.return_value.limit_items_by_id,
        "hours_since_update_until_abandoned": use_case.update.return_value.hours_since_update_until_abandoned,
        "max_abandoned_notifications_qty": use_case.update.return_value.max_abandoned_notifications_qty,
        "abandoned_cart_text": use_case.update.return_value.abandoned_cart_text,
    }


@pytest.mark.parametrize(
    ("use_case", "expected_code", "expected_error"),
    [
        pytest.param(
            {"raises": OperationForbiddenError},
            HTTPStatus.BAD_REQUEST,
            {"detail": {"code": 1001, "message": "Forbidden."}},
            id="OperationForbiddenError",
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
    response = await http_client.put(
        url=url_path,
        json={
            "max_items_qty": fake.numeric.integer_number(start=1),
            "min_cost_for_checkout": fake.numeric.integer_number(start=1),
            "limit_items_by_id": {"1": 3, "3": 6},
            "hours_since_update_until_abandoned": fake.numeric.integer_number(start=1),
            "max_abandoned_notifications_qty": fake.numeric.integer_number(start=1),
            "abandoned_cart_text": fake.text.word(),
        },
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_error
