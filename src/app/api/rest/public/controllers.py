from fastapi import APIRouter

from app.api.rest import public

public_api = APIRouter()

public_api.include_router(public.v1.items.controllers.router, prefix="/v1/items")
