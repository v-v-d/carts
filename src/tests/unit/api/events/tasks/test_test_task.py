from typing import Any

import pytest

from app.api.events.tasks.test import test_task


@pytest.fixture()
def ctx() -> dict[str, Any]:
    return {}


async def test_ok(ctx: dict[str, Any]) -> None:
    await test_task(ctx)
