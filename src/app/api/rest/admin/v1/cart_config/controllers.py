from decimal import Decimal
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Header

from app.api.rest.admin.v1.view_models import CartConfigModelView
from app.api.rest.errors import FORBIDDEN_HTTP_ERROR
from app.app_layer.interfaces.auth_system.exceptions import OperationForbiddenError
from app.app_layer.interfaces.use_cases.cart_config.dto import CartConfigInputDTO
from app.app_layer.interfaces.use_cases.cart_config.service import ICartConfigService
from app.containers import Container

router = APIRouter()


@router.get("")
@inject
async def retrieve(
    auth_data: str = Header(..., alias="Authorization"),
    use_case: ICartConfigService = Depends(Provide[Container.cart_config_service]),
) -> CartConfigModelView:
    try:
        result = await use_case.retrieve(auth_data=auth_data)
    except OperationForbiddenError:
        raise FORBIDDEN_HTTP_ERROR

    return CartConfigModelView.model_validate(result)


@router.put("")
@inject
async def update(
    max_items_qty: Annotated[int, Body()],
    min_cost_for_checkout: Annotated[Decimal, Body()],
    limit_items_by_id: Annotated[dict[int, int], Body()],
    auth_data: str = Header(..., alias="Authorization"),
    use_case: ICartConfigService = Depends(Provide[Container.cart_config_service]),
) -> CartConfigModelView:
    try:
        result = await use_case.update(
            data=CartConfigInputDTO(
                max_items_qty=max_items_qty,
                min_cost_for_checkout=min_cost_for_checkout,
                limit_items_by_id=limit_items_by_id,
                auth_data=auth_data,
            )
        )
    except OperationForbiddenError:
        raise FORBIDDEN_HTTP_ERROR

    return CartConfigModelView.model_validate(result)
