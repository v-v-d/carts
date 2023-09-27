from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, status

from app.interfaces.clients.products.exceptions import ProductsClientError
from app.interfaces.services.items.dto import ItemOutputDTO, ItemInputDTO
from app.interfaces.services.items.service import IItemsService
from containers import Container

router = APIRouter()


@router.get("/")
@inject
async def items_list(
    service: IItemsService = Depends(Provide[Container.items_service]),
) -> list[ItemOutputDTO]:
    return await service.get_items()


@router.post("/", response_model=ItemOutputDTO)
@inject
async def add_item(
    item: ItemInputDTO,
    service: IItemsService = Depends(Provide[Container.items_service]),
) -> ItemOutputDTO:
    try:
        return await service.add_item(item)
    except ProductsClientError:
        raise HTTPException(status_code=status.HTTP_424_FAILED_DEPENDENCY)

