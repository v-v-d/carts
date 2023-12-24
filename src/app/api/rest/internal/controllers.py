from fastapi import APIRouter

from app.api.rest import internal

internal_api = APIRouter()

internal_api.include_router(internal.v1.carts.controllers.router, prefix="/v1/carts")
