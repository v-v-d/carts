from fastapi import FastAPI

from app.api.rest.admin.controllers import admin_api
from app.api.rest.internal.controllers import internal_api
from app.api.rest.public.controllers import public_api


def init_rest_api(app: FastAPI) -> FastAPI:
    app.include_router(public_api, prefix="/api", tags=["Public API"])
    app.include_router(internal_api, prefix="/api/internal", tags=["Internal API"])
    app.include_router(admin_api, prefix="/api/admin", tags=["Admin API"])

    return app
