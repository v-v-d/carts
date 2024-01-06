from dependency_injector.wiring import Provide, inject

from app.app_layer.use_cases.cart_items.add_item import AddCartItemUseCase
from app.app_layer.use_cases.cart_items.dto import AddItemToCartInputDTO
from app.containers import Container


@inject
async def run_add_item_command(
    data: AddItemToCartInputDTO,
    use_case: AddCartItemUseCase = Provide[Container.add_cart_item_use_case],
) -> None:
    await use_case.execute(data=data)
