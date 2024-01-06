from datetime import datetime
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Header

from app.api.rest.admin.v1.view_models import CartListViewModel, CartViewModel
from app.api.rest.errors import (
    ACTIVE_CART_ALREADY_EXISTS_HTTP_ERROR,
    AUTHORIZATION_HTTP_ERROR,
    FORBIDDEN_HTTP_ERROR,
)
from app.app_layer.interfaces.auth_system.exceptions import (
    InvalidAuthDataError,
    OperationForbiddenError,
)
from app.app_layer.use_cases.carts.cart_list import CartListUseCase
from app.app_layer.use_cases.carts.create_cart import CreateCartUseCase
from app.app_layer.use_cases.carts.dto import CartCreateByUserIdInputDTO, CartListInputDTO
from app.containers import Container
from app.domain.interfaces.repositories.carts.exceptions import (
    ActiveCartAlreadyExistsError,
)

router = APIRouter()


@router.post("")
@inject
async def create(
    user_id: Annotated[int, Body()],
    auth_data: str = Header(..., alias="Authorization"),
    use_case: CreateCartUseCase = Depends(Provide[Container.create_cart_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.create_by_user_id(
            data=CartCreateByUserIdInputDTO(
                auth_data=auth_data,
                user_id=user_id,
            )
        )
    except InvalidAuthDataError:
        raise AUTHORIZATION_HTTP_ERROR
    except ActiveCartAlreadyExistsError:
        raise ACTIVE_CART_ALREADY_EXISTS_HTTP_ERROR
    except OperationForbiddenError:
        raise FORBIDDEN_HTTP_ERROR

    return CartViewModel.model_validate(result)


@router.get("")
@inject
async def get_list(
    page_size: int,
    created_at: datetime | None = None,
    auth_data: str = Header(..., alias="Authorization"),
    use_case: CartListUseCase = Depends(Provide[Container.cart_list_use_case]),
) -> CartListViewModel:
    try:
        result = await use_case.execute(
            data=CartListInputDTO(
                page_size=page_size,
                created_at=created_at,
                auth_data=auth_data,
            ),
        )
    except InvalidAuthDataError:
        raise AUTHORIZATION_HTTP_ERROR
    except OperationForbiddenError:
        raise FORBIDDEN_HTTP_ERROR

    return CartListViewModel(
        items=result,
        page_size=page_size,
    )
