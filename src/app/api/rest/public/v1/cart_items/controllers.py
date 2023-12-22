from decimal import Decimal
from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Header, HTTPException, status

from app.api.rest.public.v1.errors import (
    ADD_CART_ITEM_ERROR,
    ADD_CART_ITEM_MAX_QTY_ERROR,
    AUTHORIZATION_ERROR,
    CART_OPERATION_FORBIDDEN,
    FORBIDDEN_ERROR,
    RETRIEVE_CART_ERROR,
    UPDATE_CART_ITEM_ERROR,
    UPDATE_CART_ITEM_MAX_QTY_ERROR,
)
from app.api.rest.public.v1.view_models import CartViewModel
from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.app_layer.interfaces.use_cases.cart_items.add_item import IAddCartItemUseCase
from app.app_layer.interfaces.use_cases.cart_items.delete_item import (
    IDeleteCartItemUseCase,
)
from app.app_layer.interfaces.use_cases.cart_items.dto import (
    AddItemToCartInputDTO,
    ClearCartInputDTO,
    DeleteCartItemInputDTO,
    UpdateCartItemInputDTO,
)
from app.app_layer.interfaces.use_cases.cart_items.update_item import (
    IUpdateCartItemUseCase,
)
from app.app_layer.interfaces.use_cases.carts.clear_cart import IClearCartUseCase
from app.containers import Container
from app.domain.cart_items.exceptions import MinQtyLimitExceededError
from app.domain.carts.exceptions import (
    CartItemDoesNotExistError,
    MaxItemsQtyLimitExceeded,
    NotOwnedByUserError,
    OperationForbiddenError,
)
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError

router = APIRouter()


@router.post("")
@inject
async def add_item(
    cart_id: UUID,
    item_id: Annotated[int, Body()],
    qty: Annotated[Decimal, Body()],
    auth_data: str = Header(..., alias="Authorization"),
    use_case: IAddCartItemUseCase = Depends(Provide[Container.add_cart_item_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(
            data=AddItemToCartInputDTO(
                id=item_id,
                qty=qty,
                auth_data=auth_data,
                cart_id=cart_id,
            ),
        )
    except InvalidAuthDataError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTHORIZATION_ERROR,
        )
    except CartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=RETRIEVE_CART_ERROR
        )
    except NotOwnedByUserError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=FORBIDDEN_ERROR
        )
    except OperationForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=CART_OPERATION_FORBIDDEN
        )
    except (ProductsClientError, MinQtyLimitExceededError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ADD_CART_ITEM_ERROR
        )
    except MaxItemsQtyLimitExceeded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ADD_CART_ITEM_MAX_QTY_ERROR
        )

    return CartViewModel.model_validate(result)


@router.put("/{item_id}")
@inject
async def update_item(
    cart_id: UUID,
    item_id: int,
    qty: Annotated[Decimal, Body()],
    auth_data: str = Header(..., alias="Authorization"),
    use_case: IUpdateCartItemUseCase = Depends(
        Provide[Container.update_cart_item_use_case]
    ),
) -> CartViewModel:
    try:
        result = await use_case.execute(
            data=UpdateCartItemInputDTO(
                item_id=item_id,
                cart_id=cart_id,
                qty=qty,
                auth_data=auth_data,
            ),
        )
    except InvalidAuthDataError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTHORIZATION_ERROR,
        )
    except CartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=RETRIEVE_CART_ERROR
        )
    except NotOwnedByUserError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=FORBIDDEN_ERROR
        )
    except OperationForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=CART_OPERATION_FORBIDDEN
        )
    except (CartItemDoesNotExistError, MinQtyLimitExceededError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=UPDATE_CART_ITEM_ERROR
        )
    except MaxItemsQtyLimitExceeded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=UPDATE_CART_ITEM_MAX_QTY_ERROR
        )

    return CartViewModel.model_validate(result)


@router.delete("/{item_id}")
@inject
async def delete_item(
    cart_id: UUID,
    item_id: int,
    auth_data: str = Header(..., alias="Authorization"),
    use_case: IDeleteCartItemUseCase = Depends(
        Provide[Container.delete_cart_item_use_case]
    ),
) -> CartViewModel:
    try:
        result = await use_case.execute(
            data=DeleteCartItemInputDTO(
                item_id=item_id,
                cart_id=cart_id,
                auth_data=auth_data,
            ),
        )
    except InvalidAuthDataError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTHORIZATION_ERROR,
        )
    except CartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=RETRIEVE_CART_ERROR
        )
    except NotOwnedByUserError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=FORBIDDEN_ERROR
        )
    except OperationForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=CART_OPERATION_FORBIDDEN
        )

    return CartViewModel.model_validate(result)


@router.delete("")
@inject
async def clear(
    cart_id: UUID,
    auth_data: str = Header(..., alias="Authorization"),
    use_case: IClearCartUseCase = Depends(Provide[Container.clear_cart_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(
            data=ClearCartInputDTO(
                cart_id=cart_id,
                auth_data=auth_data,
            )
        )
    except InvalidAuthDataError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTHORIZATION_ERROR,
        )
    except CartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=RETRIEVE_CART_ERROR
        )
    except NotOwnedByUserError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=FORBIDDEN_ERROR
        )
    except OperationForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=CART_OPERATION_FORBIDDEN
        )

    return CartViewModel.model_validate(result)
