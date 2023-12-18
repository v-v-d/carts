from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.rest.public.v1.errors import ACTIVE_CART_ALREADY_EXISTS_ERROR, RETRIEVE_CART_ERROR
from app.api.rest.public.v1.view_models import CartViewModel
from app.app_layer.interfaces.use_cases.cart_items.dto import CreateCartInputDTO
from app.app_layer.interfaces.use_cases.carts.cart_delete import ICartDeleteUseCase
from app.app_layer.interfaces.use_cases.carts.cart_retrieve import ICartRetrieveUseCase
from app.app_layer.interfaces.use_cases.carts.create_cart import ICreateCartUseCase
from app.containers import Container
from app.domain.interfaces.repositories.carts.exceptions import (
    ActiveCartAlreadyExistsError,
    CartNotFoundError,
)

router = APIRouter()


@router.post("")
@inject
async def create(
    data: CreateCartInputDTO,
    use_case: ICreateCartUseCase = Depends(Provide[Container.create_cart_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(data=data)
    except ActiveCartAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ACTIVE_CART_ALREADY_EXISTS_ERROR,
        )

    return CartViewModel.model_validate(result)


@router.get("/{cart_id}")
@inject
async def retrieve(
    cart_id: UUID,
    use_case: ICartRetrieveUseCase = Depends(Provide[Container.cart_retrieve_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(cart_id=cart_id)
    except CartNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=RETRIEVE_CART_ERROR)

    return CartViewModel.model_validate(result)


@router.post("/{cart_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def deactivate(
    cart_id: UUID,
    use_case: ICartDeleteUseCase = Depends(Provide[Container.cart_delete_use_case]),
) -> None:
    try:
        await use_case.execute(cart_id=cart_id)
    except CartNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=RETRIEVE_CART_ERROR)
