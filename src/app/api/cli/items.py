from dependency_injector.wiring import Provide, inject

from app.app_layer.interfaces.services.items.dto import ItemAddingInputDTO
from app.app_layer.interfaces.services.items.items_adding import IItemsAddingService
from app.containers import Container


@inject
async def run_add_item_command(
    item_id: int,
    qty: int,
    service: IItemsAddingService = Provide[Container.items_adding_service],
) -> None:
    await service.execute(data=ItemAddingInputDTO(id=item_id, qty=qty))
