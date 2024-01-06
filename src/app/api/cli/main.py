import asyncio
from contextlib import asynccontextmanager
from functools import wraps
from logging.config import dictConfig
from typing import Any, AsyncContextManager, Callable
from uuid import UUID

import typer

from app.api import cli
from app.api.cli.items import run_add_item_command
from app.app_layer.use_cases.cart_items.dto import AddItemToCartInputDTO
from app.config import Config
from app.containers import Container
from app.logging import ctx, get_logging_config

app = typer.Typer()


def coro(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@asynccontextmanager
async def container() -> AsyncContextManager[Container]:  # pragma: no cover
    config = Config()
    dictConfig(
        config=get_logging_config(
            transaction_ctx=ctx,
            config=config.LOGGING,
        ),
    )

    async with Container.lifespan(wireable_packages=[cli]) as cont:
        yield cont


app.container = container


@app.command()
@coro
async def add_item(item_id: int, qty: int, cart_id: UUID, auth_data: str) -> None:
    async with app.container():
        await run_add_item_command(
            data=AddItemToCartInputDTO(
                id=item_id,
                qty=qty,
                cart_id=cart_id,
                auth_data=auth_data,
            ),
        )


@app.command()
def dummy() -> None:  # pragma: no cover
    print("dummy")  # noqa: T201


if __name__ == "__main__":
    app()
