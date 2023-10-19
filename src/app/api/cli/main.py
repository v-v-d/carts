import asyncio
from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncIterator, Callable, Any

import typer

from app.api import cli
from app.api.cli.items import run_add_item_command
from app.containers import Container

app = typer.Typer()


def coro(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@asynccontextmanager
async def container() -> AsyncIterator[None]:
    _container = Container()
    _container.wire(packages=[cli])

    await _container.init_resources()

    try:
        yield
    finally:
        await _container.shutdown_resources()


@app.command()
@coro
async def add_item(item_id: int, qty: int) -> None:
    async with container():
        await run_add_item_command(item_id, qty)


@app.command()
def dummy() -> None:
    print("dummy")  # noqa: T201


if __name__ == "__main__":
    app()
