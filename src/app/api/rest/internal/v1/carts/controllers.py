from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.api.rest.errors import (
    CART_CANT_BE_COMPLETED_HTTP_ERROR,
    CART_CANT_BE_LOCKED_HTTP_ERROR,
    CART_CANT_BE_UNLOCKED_HTTP_ERROR,
    CART_IN_PROCESS_HTTP_ERROR,
    RETRIEVE_CART_HTTP_ERROR,
)
from app.api.rest.internal.v1.view_models import CartViewModel
from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.use_cases.carts.cart_complete import CompleteCartUseCase
from app.app_layer.use_cases.carts.cart_lock import LockCartUseCase
from app.app_layer.use_cases.carts.cart_unlock import UnlockCartUseCase
from app.containers import Container
from app.domain.carts.exceptions import CantBeLockedError, ChangeStatusError
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError

router = APIRouter()


@router.post("/{cart_id}/lock")
@inject
async def lock(
    cart_id: UUID,
    use_case: LockCartUseCase = Depends(Provide[Container.lock_cart_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(cart_id=cart_id)
    except AlreadyLockedError:
        raise CART_IN_PROCESS_HTTP_ERROR
    except CartNotFoundError:
        raise RETRIEVE_CART_HTTP_ERROR
    except (CantBeLockedError, ChangeStatusError):
        raise CART_CANT_BE_LOCKED_HTTP_ERROR

    return CartViewModel.model_validate(result)


@router.post("/{cart_id}/unlock")
@inject
async def unlock(
    cart_id: UUID,
    use_case: UnlockCartUseCase = Depends(Provide[Container.unlock_cart_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(cart_id=cart_id)
    except AlreadyLockedError:
        raise CART_IN_PROCESS_HTTP_ERROR
    except CartNotFoundError:
        raise RETRIEVE_CART_HTTP_ERROR
    except ChangeStatusError:
        raise CART_CANT_BE_UNLOCKED_HTTP_ERROR

    return CartViewModel.model_validate(result)


@router.post("/{cart_id}/complete")
@inject
async def complete(
    cart_id: UUID,
    use_case: CompleteCartUseCase = Depends(Provide[Container.complete_cart_use_case]),
) -> CartViewModel:
    try:
        result = await use_case.execute(cart_id=cart_id)
    except AlreadyLockedError:
        raise CART_IN_PROCESS_HTTP_ERROR
    except CartNotFoundError:
        raise RETRIEVE_CART_HTTP_ERROR
    except ChangeStatusError:
        raise CART_CANT_BE_COMPLETED_HTTP_ERROR

    return CartViewModel.model_validate(result)
