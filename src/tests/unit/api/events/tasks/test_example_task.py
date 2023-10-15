from typing import Any

import pytest

from app.api.events.tasks.example import example_task


@pytest.fixture()
def ctx() -> dict[str, Any]:
    return {}


async def test_ok(ctx: dict[str, Any]) -> None:
    await example_task(ctx)
