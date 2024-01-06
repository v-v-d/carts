from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Header, status

from app.api.rest.errors import (
    ACTIVE_CART_ALREADY_EXISTS_HTTP_ERROR,
    AUTHORIZATION_HTTP_ERROR,
    CART_IN_PROCESS_HTTP_ERROR,
    CART_OPERATION_FORBIDDEN_HTTP_ERROR,
    COUPON_ALREADY_APPLIED_HTTP_ERROR,
    COUPON_APPLYING_HTTP_ERROR,
    DELETE_CART_HTTP_ERROR,
    RETRIEVE_CART_HTTP_ERROR,
)
from app.api.rest.public.v1.view_models import CartViewModel
from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.clients.coupons.exceptions import CouponsClientError
from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.use_cases.carts.cart_apply_coupon import CartApplyCouponUseCase
from app.app_layer.use_cases.carts.cart_delete import CartDeleteUseCase
from app.app_layer.use_cases.carts.cart_remove_coupon import CartRemoveCouponUseCase
from app.app_layer.use_cases.carts.cart_retrieve import CartRetrieveUseCase
from app.app_layer.use_cases.carts.create_cart import CreateCartUseCase
from app.app_layer.use_cases.carts.dto import (
    CartApplyCouponInputDTO,
    CartDeleteInputDTO,
    CartRemoveCouponInputDTO,
    CartRetrieveInputDTO,
)
from app.containers import Container
from app.domain.carts.exceptions import (
    ChangeStatusError,
    CouponAlreadyAppliedError,
    NotOwnedByUserError,
    OperationForbiddenError,
)
from app.domain.interfaces.repositories.carts.exceptions import (
    ActiveCartAlreadyExistsError,
    CartNotFoundError,
)

router = APIRouter()


@router.post("")
@inject
async def create(
    auth_data: str = Header(..., alias="Authorization"),
    use_case: CreateCartUseCase = Depends(Provide[Container.create_cart_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.create_by_auth_data(auth_data=auth_data)
    except InvalidAuthDataError:
        raise AUTHORIZATION_HTTP_ERROR
    except ActiveCartAlreadyExistsError:
        raise ACTIVE_CART_ALREADY_EXISTS_HTTP_ERROR

    return CartViewModel.model_validate(result)


@router.get("/{cart_id}")
@inject
async def retrieve(
    cart_id: UUID,
    auth_data: str = Header(..., alias="Authorization"),
    use_case: CartRetrieveUseCase = Depends(Provide[Container.cart_retrieve_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(
            data=CartRetrieveInputDTO(
                auth_data=auth_data,
                cart_id=cart_id,
            ),
        )
    except InvalidAuthDataError:
        raise AUTHORIZATION_HTTP_ERROR
    except (CartNotFoundError, NotOwnedByUserError):
        raise RETRIEVE_CART_HTTP_ERROR

    return CartViewModel.model_validate(result)


@router.post("/{cart_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def deactivate(
    cart_id: UUID,
    auth_data: str = Header(..., alias="Authorization"),
    use_case: CartDeleteUseCase = Depends(Provide[Container.cart_delete_use_case]),
) -> None:
    try:
        await use_case.execute(
            data=CartDeleteInputDTO(auth_data=auth_data, cart_id=cart_id)
        )
    except AlreadyLockedError:
        raise CART_IN_PROCESS_HTTP_ERROR
    except InvalidAuthDataError:
        raise AUTHORIZATION_HTTP_ERROR
    except (CartNotFoundError, NotOwnedByUserError):
        raise RETRIEVE_CART_HTTP_ERROR
    except ChangeStatusError:
        raise DELETE_CART_HTTP_ERROR


@router.post("/{cart_id}/apply-coupon")
@inject
async def apply_coupon(
    cart_id: UUID,
    coupon_name: Annotated[str, Body()],
    auth_data: str = Header(..., alias="Authorization"),
    use_case: CartApplyCouponUseCase = Depends(
        Provide[Container.cart_apply_coupon_use_case]
    ),
) -> CartViewModel:
    try:
        result = await use_case.execute(
            data=CartApplyCouponInputDTO(
                cart_id=cart_id,
                coupon_name=coupon_name,
                auth_data=auth_data,
            )
        )
    except AlreadyLockedError:
        raise CART_IN_PROCESS_HTTP_ERROR
    except InvalidAuthDataError:
        raise AUTHORIZATION_HTTP_ERROR
    except (CartNotFoundError, NotOwnedByUserError):
        raise RETRIEVE_CART_HTTP_ERROR
    except CouponAlreadyAppliedError:
        raise COUPON_ALREADY_APPLIED_HTTP_ERROR
    except CouponsClientError:
        raise COUPON_APPLYING_HTTP_ERROR
    except OperationForbiddenError:
        raise CART_OPERATION_FORBIDDEN_HTTP_ERROR

    return CartViewModel.model_validate(result)


@router.post("/{cart_id}/remove-coupon")
@inject
async def remove_coupon(
    cart_id: UUID,
    auth_data: str = Header(..., alias="Authorization"),
    use_case: CartRemoveCouponUseCase = Depends(
        Provide[Container.cart_remove_coupon_use_case]
    ),
) -> CartViewModel:
    try:
        result = await use_case.execute(
            data=CartRemoveCouponInputDTO(
                cart_id=cart_id,
                auth_data=auth_data,
            )
        )
    except AlreadyLockedError:
        raise CART_IN_PROCESS_HTTP_ERROR
    except InvalidAuthDataError:
        raise AUTHORIZATION_HTTP_ERROR
    except (CartNotFoundError, NotOwnedByUserError):
        raise RETRIEVE_CART_HTTP_ERROR
    except OperationForbiddenError:
        raise CART_OPERATION_FORBIDDEN_HTTP_ERROR

    return CartViewModel.model_validate(result)
