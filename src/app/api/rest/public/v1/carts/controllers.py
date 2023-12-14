from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import TypeAdapter

from app.api.rest.public.v1.carts.errors import CART_RETRIEVE_ERROR
from app.api.rest.public.v1.view_models import CartViewModel
from app.app_layer.interfaces.use_cases.carts.cart_delete import ICartDeleteUseCase
from app.app_layer.interfaces.use_cases.carts.cart_list import ICartListUseCase
from app.app_layer.interfaces.use_cases.carts.cart_retrieve import ICartRetrieveUseCase
from app.containers import Container
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError

router = APIRouter()


@router.get("/{cart_id}")
@inject
async def retrieve(
    cart_id: UUID,
    use_case: ICartRetrieveUseCase = Depends(Provide[Container.cart_retrieve_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(cart_id=cart_id)
    except CartNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=CART_RETRIEVE_ERROR)

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=CART_RETRIEVE_ERROR)


@router.get("")
@inject
async def get_list(
    use_case: ICartListUseCase = Depends(Provide[Container.cart_list_use_case]),
) -> list[CartViewModel]:
    result = await use_case.execute()

    return TypeAdapter(list[CartViewModel]).validate_python(result)
