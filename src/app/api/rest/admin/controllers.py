from fastapi import APIRouter

from app.api.rest import admin

admin_api = APIRouter()

admin_api.include_router(admin.v1.carts.controllers.router, prefix="/v1/carts")
