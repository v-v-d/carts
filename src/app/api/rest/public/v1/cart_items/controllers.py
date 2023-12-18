from decimal import Decimal
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.rest.public.v1.errors import (
    ADD_CART_ITEM_ERROR,
    DELETE_CART_ITEM_ERROR,
    RETRIEVE_CART_ERROR,
)
from app.api.rest.public.v1.view_models import CartViewModel
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.app_layer.interfaces.use_cases.cart_items.add_item import IAddCartItemUseCase
from app.app_layer.interfaces.use_cases.cart_items.delete_item import IDeleteCartItemUseCase
from app.app_layer.interfaces.use_cases.cart_items.dto import (
    AddItemToCartInputDTO,
    DeleteCartItemInputDTO,
    UpdateCartItemInputDTO,
)
from app.app_layer.interfaces.use_cases.cart_items.update_item import IUpdateCartItemUseCase
from app.app_layer.interfaces.use_cases.carts.clear_cart import IClearCartUseCase
from app.containers import Container
from app.domain.cart_items.exceptions import MinQtyLimitExceededError
from app.domain.carts.exceptions import CartItemDoesNotExistError
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError

router = APIRouter()


@router.post("")
@inject
async def add_item(
    cart_id: UUID,
    data: AddItemToCartInputDTO,
    use_case: IAddCartItemUseCase = Depends(Provide[Container.add_cart_item_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(cart_id=cart_id, data=data)
    except CartNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=RETRIEVE_CART_ERROR)
    except (ProductsClientError, MinQtyLimitExceededError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ADD_CART_ITEM_ERROR)

    return CartViewModel.model_validate(result)


@router.put("/{item_id}")
@inject
async def update_item(
    cart_id: UUID,
    item_id: int,
    qty: Decimal,
    use_case: IUpdateCartItemUseCase = Depends(Provide[Container.update_cart_item_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(
            data=UpdateCartItemInputDTO(
                item_id=item_id,
                cart_id=cart_id,
                qty=qty,
            ),
        )
    except CartNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=RETRIEVE_CART_ERROR)
    except CartItemDoesNotExistError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=DELETE_CART_ITEM_ERROR)

    return CartViewModel.model_validate(result)


@router.delete("/{item_id}")
@inject
async def delete_item(
    cart_id: UUID,
    item_id: int,
    use_case: IDeleteCartItemUseCase = Depends(Provide[Container.delete_cart_item_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(
            data=DeleteCartItemInputDTO(
                item_id=item_id,
                cart_id=cart_id,
            ),
        )
    except CartNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=RETRIEVE_CART_ERROR)

    return CartViewModel.model_validate(result)


@router.delete("")
@inject
async def clear(
    cart_id: UUID,
    use_case: IClearCartUseCase = Depends(Provide[Container.clear_cart_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(cart_id=cart_id)
    except CartNotFoundError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=RETRIEVE_CART_ERROR)

    return CartViewModel.model_validate(result)
