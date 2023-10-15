from contextlib import asynccontextmanager
from typing import AsyncContextManager

from fastapi import FastAPI

from app.api import rest
from app.api.rest.controllers import init_rest_api
from app.containers import Container


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncContextManager[None]:
    app_.container = Container()
    app_.container.wire(packages=[rest])
    await app_.container.init_resources()

    yield

    await app_.container.shutdown_resources()


app = FastAPI(lifespan=lifespan)
init_rest_api(app)
