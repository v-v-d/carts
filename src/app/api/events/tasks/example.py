from typing import Any
from uuid import UUID

from dependency_injector.wiring import Provide, inject

from app.app_layer.interfaces.use_cases.carts.cart_retrieve import ICartRetrieveUseCase
from app.containers import Container


@inject
async def example_task(
    _ctx: [str, Any],
    auth_data: str,
    cart_id: UUID,
    use_case: ICartRetrieveUseCase = Provide[Container.cart_retrieve_use_case],
) -> None:
    await use_case.execute(auth_data=auth_data, cart_id=cart_id)
