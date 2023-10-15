from typing import Any

from dependency_injector.wiring import inject


@inject
async def example_task(ctx: [str, Any]) -> None:
    print("Hello from worker example task")  # noqa: T201
