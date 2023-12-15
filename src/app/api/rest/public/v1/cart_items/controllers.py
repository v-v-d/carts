from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.rest.public.v1.cart_items.errors import ITEM_ADDING_ERROR
from app.api.rest.public.v1.cart_items.view_models import CartItemAddingViewModel
from app.app_layer.interfaces.clients.products.exceptions import ProductsClientError
from app.app_layer.interfaces.task_producer import ITaskProducer
from app.app_layer.interfaces.use_cases.items.dto import ItemAddingInputDTO
from app.app_layer.interfaces.use_cases.items.items_adding import IItemsAddingUseCase
from app.containers import Container
from app.domain.interfaces.repositories.items.exceptions import ItemAlreadyExists
from app.domain.items.exceptions import QtyValidationError

router = APIRouter()


@router.post("/", response_model=CartItemAddingViewModel)
@inject
async def add_item_to_cart(
    item: ItemAddingInputDTO,
    use_case: IItemsAddingUseCase = Depends(Provide[Container.items_adding_use_case]),
) -> CartItemAddingViewModel:
    try:
        result = await use_case.execute(item)
    except (ProductsClientError, QtyValidationError, ItemAlreadyExists):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ITEM_ADDING_ERROR)

    return CartItemAddingViewModel.model_validate(result)


@router.post("/produce", status_code=status.HTTP_202_ACCEPTED)
@inject
async def produce(
    task_producer: ITaskProducer = Depends(Provide[Container.events.task_producer]),
) -> None:
    await task_producer.enqueue_example_task()
