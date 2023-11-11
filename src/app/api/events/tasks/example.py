from typing import Any

from dependency_injector.wiring import Provide, inject

from app.app_layer.interfaces.services.items.items_list import IItemsListService
from app.containers import Container


@inject
async def example_task(
    ctx: [str, Any],
    service: IItemsListService = Provide[Container.items_list_service],
) -> None:
    await service.execute()
