from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.rest.public.v1.errors import (
    ACTIVE_CART_ALREADY_EXISTS_ERROR,
    AUTHORIZATION_ERROR,
    DELETE_CART_ERROR,
    RETRIEVE_CART_ERROR,
)
from app.api.rest.public.v1.view_models import CartViewModel
from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.use_cases.carts.cart_delete import ICartDeleteUseCase
from app.app_layer.interfaces.use_cases.carts.cart_retrieve import ICartRetrieveUseCase
from app.app_layer.interfaces.use_cases.carts.create_cart import ICreateCartUseCase
from app.containers import Container
from app.domain.carts.exceptions import ChangeStatusError, NotOwnedByUserError
from app.domain.interfaces.repositories.carts.exceptions import (
    ActiveCartAlreadyExistsError,
    CartNotFoundError,
)

router = APIRouter()


@router.post("")
@inject
async def create(
    auth_data: str = Header(..., alias="Authorization"),
    use_case: ICreateCartUseCase = Depends(Provide[Container.create_cart_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(auth_data=auth_data)
    except InvalidAuthDataError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTHORIZATION_ERROR,
        )
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
    auth_data: str = Header(..., alias="Authorization"),
    use_case: ICartRetrieveUseCase = Depends(Provide[Container.cart_retrieve_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(auth_data=auth_data, cart_id=cart_id)
    except InvalidAuthDataError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTHORIZATION_ERROR,
        )
    except (CartNotFoundError, NotOwnedByUserError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=RETRIEVE_CART_ERROR,
        )

    return CartViewModel.model_validate(result)


@router.post("/{cart_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def deactivate(
    cart_id: UUID,
    auth_data: str = Header(..., alias="Authorization"),
    use_case: ICartDeleteUseCase = Depends(Provide[Container.cart_delete_use_case]),
) -> None:
    try:
        await use_case.execute(auth_data=auth_data, cart_id=cart_id)
    except InvalidAuthDataError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTHORIZATION_ERROR,
        )
    except (CartNotFoundError, NotOwnedByUserError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=RETRIEVE_CART_ERROR
        )
    except ChangeStatusError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DELETE_CART_ERROR,
        )
