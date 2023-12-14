from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.rest.public.v1.carts.errors import CART_RETRIEVE_ERROR
from app.api.rest.public.v1.view_models import CartViewModel
from app.app_layer.interfaces.services.carts.cart_retrieve import ICartRetrieveService
from app.containers import Container
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError

router = APIRouter()


@router.get("/{cart_id}")
@inject
async def retrieve(
    cart_id: UUID,
    service: ICartRetrieveService = Depends(Provide[Container.cart_retrieve_service]),
) -> CartViewModel:
    try:
        result = await service.execute(cart_id=cart_id)
    except CartNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=CART_RETRIEVE_ERROR)

    return CartViewModel.model_validate(result)
