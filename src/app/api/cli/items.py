from dependency_injector.wiring import Provide, inject

from app.app_layer.interfaces.use_cases.items.dto import ItemAddingInputDTO
from app.app_layer.interfaces.use_cases.items.items_adding import IItemsAddingUseCase
from app.containers import Container


@inject
async def run_add_item_command(
    item_id: int,
    qty: int,
    use_case: IItemsAddingUseCase = Provide[Container.items_adding_use_case],
) -> None:
    await use_case.execute(data=ItemAddingInputDTO(id=item_id, qty=qty))
