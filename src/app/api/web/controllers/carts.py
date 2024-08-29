from pathlib import Path
from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, status, Cookie, Form, Header, HTTPException
from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.clients.coupons.exceptions import CouponsClientError
from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.use_cases.carts.cart_active_retrieve import CartActiveRetrieveUseCase
from app.app_layer.use_cases.carts.cart_apply_coupon import CartApplyCouponUseCase
from app.app_layer.use_cases.carts.cart_delete import CartDeleteUseCase
from app.app_layer.use_cases.carts.cart_remove_coupon import CartRemoveCouponUseCase
from app.app_layer.use_cases.carts.create_cart import CreateCartUseCase
from app.app_layer.use_cases.carts.dto import (
    CartApplyCouponInputDTO,
    CartDeleteInputDTO,
    CartRemoveCouponInputDTO,
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

templates_path = Path(__file__).parent.parent / "views"
templates = Jinja2Templates(directory=str(templates_path))


@inject
async def create(
    request: Request,
    auth_data: str = Cookie(..., alias="Authorization"),
    use_case: CreateCartUseCase = Depends(Provide[Container.create_cart_use_case]),
) -> templates.TemplateResponse:
    try:
        cart = await use_case.create_by_auth_data(auth_data=auth_data)
    except InvalidAuthDataError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except ActiveCartAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return templates.TemplateResponse(
        name="carts/cart.html",
        context={"cart": cart, "request": request},
    )


@inject
async def retrieve_active(
    request: Request,
    auth_data: str = Cookie(..., alias="Authorization"),
    hx_request: Annotated[bool, Header()] = False,
    use_case: CartActiveRetrieveUseCase = Depends(Provide[Container.cart_active_retrieve_use_case]),
) -> templates.TemplateResponse:
    if not hx_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        cart = await use_case.execute(auth_data=auth_data)
    except InvalidAuthDataError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except (CartNotFoundError, NotOwnedByUserError):
        return templates.TemplateResponse(
            name="carts/cart.html",
            context={"request": request},
        )

    return templates.TemplateResponse(
        name="carts/cart.html",
        context={"cart": cart, "request": request},
    )


@inject
async def deactivate(
    request: Request,
    cart_id: UUID,
    auth_data: str = Cookie(..., alias="Authorization"),
    hx_request: Annotated[bool, Header()] = False,
    use_case: CartDeleteUseCase = Depends(Provide[Container.cart_delete_use_case]),
) -> templates.TemplateResponse:
    if not hx_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        cart = await use_case.execute(
            data=CartDeleteInputDTO(auth_data=auth_data, cart_id=cart_id)
        )
    except (AlreadyLockedError, ChangeStatusError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except InvalidAuthDataError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except (CartNotFoundError, NotOwnedByUserError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        name="carts/cart.html",
        context={"request": request},
    )


@inject
async def apply_coupon(
    request: Request,
    cart_id: UUID,
    coupon_name: Annotated[str, Form()],
    auth_data: str = Cookie(..., alias="Authorization"),
    hx_request: Annotated[bool, Header()] = False,
    use_case: CartApplyCouponUseCase = Depends(
        Provide[Container.cart_apply_coupon_use_case]
    ),
) -> templates.TemplateResponse:
    if not hx_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        cart = await use_case.execute(
            data=CartApplyCouponInputDTO(
                cart_id=cart_id,
                coupon_name=coupon_name,
                auth_data=auth_data,
            )
        )
    except InvalidAuthDataError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except (CartNotFoundError, NotOwnedByUserError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except (
        AlreadyLockedError,
        CouponAlreadyAppliedError,
        CouponsClientError,
        OperationForbiddenError,
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return templates.TemplateResponse(
        name="carts/cart.html",
        context={"cart": cart, "request": request},
    )


@inject
async def remove_coupon(
    request: Request,
    cart_id: UUID,
    auth_data: str = Cookie(..., alias="Authorization"),
    hx_request: Annotated[bool, Header()] = False,
    use_case: CartRemoveCouponUseCase = Depends(
        Provide[Container.cart_remove_coupon_use_case]
    ),
) -> templates.TemplateResponse:
    if not hx_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        cart = await use_case.execute(
            data=CartRemoveCouponInputDTO(
                cart_id=cart_id,
                auth_data=auth_data,
            )
        )
    except (AlreadyLockedError, OperationForbiddenError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except InvalidAuthDataError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except (CartNotFoundError, NotOwnedByUserError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        name="carts/cart.html",
        context={"cart": cart, "request": request},
    )
