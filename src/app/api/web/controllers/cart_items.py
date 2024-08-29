from decimal import Decimal
from pathlib import Path
from typing import Annotated
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Cookie, HTTPException, status, Request, Form, Header
from fastapi.templating import Jinja2Templates

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

templates_path = Path(__file__).parent.parent / "views"
templates = Jinja2Templates(directory=str(templates_path))


@inject
async def add_item(
    request: Request,
    cart_id: UUID,
    item_id: Annotated[int, Form()],
    qty: Annotated[Decimal, Form()],
    auth_data: str = Cookie(..., alias="Authorization"),
    hx_request: Annotated[bool, Header()] = False,
    use_case: AddCartItemUseCase = Depends(Provide[Container.add_cart_item_use_case]),
) -> templates.TemplateResponse:
    if not hx_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        cart = await use_case.execute(
            data=AddItemToCartInputDTO(
                id=item_id,
                qty=qty,
                auth_data=auth_data,
                cart_id=cart_id,
            ),
        )
    except (
        AlreadyLockedError,
        OperationForbiddenError,
        ProductsClientError,
        MinQtyLimitExceededError,
        SpecificItemQtyLimitExceeded,
        MaxItemsQtyLimitExceeded,
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except InvalidAuthDataError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except (CartNotFoundError, NotOwnedByUserError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        name="carts/cart.html",
        context={"cart": cart, "request": request},
    )


@inject
async def update_item(
    request: Request,
    cart_id: UUID,
    item_id: int,
    qty: Annotated[Decimal, Form()],
    auth_data: str = Cookie(..., alias="Authorization"),
    hx_request: Annotated[bool, Header()] = False,
    use_case: UpdateCartItemUseCase = Depends(
        Provide[Container.update_cart_item_use_case]
    ),
) -> templates.TemplateResponse:
    if not hx_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        cart = await use_case.execute(
            data=UpdateCartItemInputDTO(
                item_id=item_id,
                cart_id=cart_id,
                qty=qty,
                auth_data=auth_data,
            ),
        )
    except (
        AlreadyLockedError,
        OperationForbiddenError,
        CartItemDoesNotExistError,
        MinQtyLimitExceededError,
        SpecificItemQtyLimitExceeded,
        MaxItemsQtyLimitExceeded,
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except InvalidAuthDataError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except (CartNotFoundError, NotOwnedByUserError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        name="carts/cart.html",
        context={"cart": cart, "request": request},
    )


@inject
async def delete_item(
    request: Request,
    cart_id: UUID,
    item_id: int,
    auth_data: str = Cookie(..., alias="Authorization"),
    hx_request: Annotated[bool, Header()] = False,
    use_case: DeleteCartItemUseCase = Depends(
        Provide[Container.delete_cart_item_use_case]
    ),
) -> templates.TemplateResponse:
    if not hx_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        cart = await use_case.execute(
            data=DeleteCartItemInputDTO(
                item_id=item_id,
                cart_id=cart_id,
                auth_data=auth_data,
            ),
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


@inject
async def clear(
    request: Request,
    cart_id: UUID,
    auth_data: str = Cookie(..., alias="Authorization"),
    hx_request: Annotated[bool, Header()] = False,
    use_case: ClearCartUseCase = Depends(Provide[Container.clear_cart_use_case]),
) -> templates.TemplateResponse:
    if not hx_request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        cart = await use_case.execute(
            data=ClearCartInputDTO(
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
