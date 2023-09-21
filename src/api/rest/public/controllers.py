from fastapi import APIRouter

from api.rest.public import v1

public_api = APIRouter()

public_api.include_router(v1.test.router, prefix="/v1/test")
