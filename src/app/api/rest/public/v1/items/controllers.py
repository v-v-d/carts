from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import TypeAdapter

from app.api.rest.public.v1.items.errors import ITEM_ADDING_ERROR
from app.api.rest.public.v1.items.view_models import ItemAddingViewModel, ItemListViewModel
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.app_layer.interfaces.repositories.items.exceptions import ItemAlreadyExists
from app.app_layer.interfaces.services.items.dto import ItemAddingInputDTO
from app.app_layer.interfaces.services.items.items_adding import IItemsAddingService
from app.app_layer.interfaces.services.items.items_list import IItemsListService
from app.app_layer.interfaces.task_producer import ITaskProducer
from app.containers import Container
from app.domain.items.exceptions import QtyValidationError

router = APIRouter()


@router.get("/")
@inject
async def items_list(
    service: IItemsListService = Depends(Provide[Container.items_list_service]),
) -> list[ItemListViewModel]:
    result = await service.execute()

    return TypeAdapter(list[ItemListViewModel]).validate_python(result)


@router.post("/", response_model=ItemAddingViewModel)
@inject
async def add_item(
    item: ItemAddingInputDTO,
    service: IItemsAddingService = Depends(Provide[Container.items_adding_service]),
) -> ItemAddingViewModel:
    try:
        result = await service.execute(item)
    except (ProductsClientError, QtyValidationError, ItemAlreadyExists):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ITEM_ADDING_ERROR)

    return ItemAddingViewModel.model_validate(result)


@router.post("/produce", status_code=status.HTTP_202_ACCEPTED)
@inject
async def produce(
    task_producer: ITaskProducer = Depends(Provide[Container.events.task_producer]),
) -> None:
    await task_producer.enqueue_test_task()
