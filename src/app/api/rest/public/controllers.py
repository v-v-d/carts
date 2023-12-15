from fastapi import APIRouter

from app.api.rest import public

public_api = APIRouter()

public_api.include_router(public.v1.cart_items.controllers.router, prefix="/v1/cart_items")
public_api.include_router(public.v1.carts.controllers.router, prefix="/v1/carts")
