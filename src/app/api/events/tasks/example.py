from typing import Any
from uuid import UUID

from dependency_injector.wiring import Provide, inject

from app.app_layer.use_cases.carts.cart_retrieve import CartRetrieveUseCase
from app.app_layer.use_cases.carts.dto import CartRetrieveInputDTO
from app.containers import Container


@inject
async def example_task(
    _ctx: [str, Any],
    auth_data: str,
    cart_id: UUID,
    use_case: CartRetrieveUseCase = Provide[Container.cart_retrieve_use_case],
) -> None:
    await use_case.execute(
        data=CartRetrieveInputDTO(auth_data=auth_data, cart_id=cart_id)
    )
