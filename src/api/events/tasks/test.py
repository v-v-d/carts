from typing import Any

from dependency_injector.wiring import inject


@inject
async def test_task(ctx: [str, Any]) -> None:
    print("Hello from arq worker task")
