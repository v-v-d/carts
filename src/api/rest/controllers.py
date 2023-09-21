from fastapi import FastAPI

from api.rest.public.controllers import public_api


def init_rest_api(app: FastAPI) -> FastAPI:
    app.include_router(public_api, prefix="/api")

    return app
