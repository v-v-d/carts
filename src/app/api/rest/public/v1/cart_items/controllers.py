from decimal import Decimal
from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Header

from app.api.rest.errors import (
    ADD_CART_ITEM_HTTP_ERROR,
    AUTHORIZATION_HTTP_ERROR,
    CART_IN_PROCESS_HTTP_ERROR,
    CART_ITEM_MAX_QTY_HTTP_ERROR,
    CART_ITEM_QTY_LIMIT_EXCEEDED_HTTP_ERROR,
    CART_OPERATION_FORBIDDEN_HTTP_ERROR,
    FORBIDDEN_HTTP_ERROR,
    RETRIEVE_CART_HTTP_ERROR,
    UPDATE_CART_ITEM_HTTP_ERROR,
)
from app.api.rest.public.v1.view_models import CartViewModel
from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.use_cases.cart_items.add_item import AddCartItemUseCase
from app.app_layer.use_cases.cart_items.delete_item import DeleteCartItemUseCase
from app.app_layer.use_cases.cart_items.dto import (
    AddItemToCartInputDTO,
    ClearCartInputDTO,
    DeleteCartItemInputDTO,
    UpdateCartItemInputDTO,
)
from app.app_layer.use_cases.cart_items.update_item import UpdateCartItemUseCase
from app.app_layer.use_cases.carts.clear_cart import ClearCartUseCase
from app.containers import Container
from app.domain.cart_items.exceptions import MinQtyLimitExceededError
from app.domain.carts.exceptions import (
    CartItemDoesNotExistError,
    MaxItemsQtyLimitExceeded,
    NotOwnedByUserError,
    OperationForbiddenError,
    SpecificItemQtyLimitExceeded,
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
    use_case: AddCartItemUseCase = Depends(Provide[Container.add_cart_item_use_case]),
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
    except AlreadyLockedError:
        raise CART_IN_PROCESS_HTTP_ERROR
    except InvalidAuthDataError:
        raise AUTHORIZATION_HTTP_ERROR
    except CartNotFoundError:
        raise RETRIEVE_CART_HTTP_ERROR
    except NotOwnedByUserError:
        raise FORBIDDEN_HTTP_ERROR
    except OperationForbiddenError:
        raise CART_OPERATION_FORBIDDEN_HTTP_ERROR
    except (ProductsClientError, MinQtyLimitExceededError):
        raise ADD_CART_ITEM_HTTP_ERROR
    except SpecificItemQtyLimitExceeded as err:
        raise CART_ITEM_QTY_LIMIT_EXCEEDED_HTTP_ERROR(err)
    except MaxItemsQtyLimitExceeded:
        raise CART_ITEM_MAX_QTY_HTTP_ERROR

    return CartViewModel.model_validate(result)


@router.patch("/{item_id}")
@inject
async def update_item(
    cart_id: UUID,
    item_id: int,
    qty: Annotated[Decimal, Body()],
    auth_data: str = Header(..., alias="Authorization"),
    use_case: UpdateCartItemUseCase = Depends(
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
    except AlreadyLockedError:
        raise CART_IN_PROCESS_HTTP_ERROR
    except InvalidAuthDataError:
        raise AUTHORIZATION_HTTP_ERROR
    except CartNotFoundError:
        raise RETRIEVE_CART_HTTP_ERROR
    except NotOwnedByUserError:
        raise FORBIDDEN_HTTP_ERROR
    except OperationForbiddenError:
        raise CART_OPERATION_FORBIDDEN_HTTP_ERROR
    except (CartItemDoesNotExistError, MinQtyLimitExceededError):
        raise UPDATE_CART_ITEM_HTTP_ERROR
    except SpecificItemQtyLimitExceeded as err:
        raise CART_ITEM_QTY_LIMIT_EXCEEDED_HTTP_ERROR(err)
    except MaxItemsQtyLimitExceeded:
        raise CART_ITEM_MAX_QTY_HTTP_ERROR

    return CartViewModel.model_validate(result)


@router.delete("/{item_id}")
@inject
async def delete_item(
    cart_id: UUID,
    item_id: int,
    auth_data: str = Header(..., alias="Authorization"),
    use_case: DeleteCartItemUseCase = Depends(
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
    except AlreadyLockedError:
        raise CART_IN_PROCESS_HTTP_ERROR
    except InvalidAuthDataError:
        raise AUTHORIZATION_HTTP_ERROR
    except CartNotFoundError:
        raise RETRIEVE_CART_HTTP_ERROR
    except NotOwnedByUserError:
        raise FORBIDDEN_HTTP_ERROR
    except OperationForbiddenError:
        raise CART_OPERATION_FORBIDDEN_HTTP_ERROR

    return CartViewModel.model_validate(result)


@router.delete("")
@inject
async def clear(
    cart_id: UUID,
    auth_data: str = Header(..., alias="Authorization"),
    use_case: ClearCartUseCase = Depends(Provide[Container.clear_cart_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(
            data=ClearCartInputDTO(
                cart_id=cart_id,
                auth_data=auth_data,
            )
        )
    except AlreadyLockedError:
        raise CART_IN_PROCESS_HTTP_ERROR
    except InvalidAuthDataError:
        raise AUTHORIZATION_HTTP_ERROR
    except CartNotFoundError:
        raise RETRIEVE_CART_HTTP_ERROR
    except NotOwnedByUserError:
        raise FORBIDDEN_HTTP_ERROR
    except OperationForbiddenError:
        raise CART_OPERATION_FORBIDDEN_HTTP_ERROR

    return CartViewModel.model_validate(result)
