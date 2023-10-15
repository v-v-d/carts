import pytest

from app.app_layer.interfaces.services.items.items_list import IItemsListService
from app.app_layer.services.items.items_list import ItemsListService
from app.domain.items.entities import Item
from tests.environment.unit_of_work import TestUow


@pytest.fixture()
def service(uow: TestUow) -> IItemsListService:
    return ItemsListService(uow=uow)


async def test_ok(service: IItemsListService, existing_item: Item) -> None:
    result = await service.execute()

    assert len(result) == 1
    assert result[0].id == existing_item.id
    assert result[0].qty == existing_item.qty
    assert result[0].name == existing_item.name
    assert result[0].price == existing_item.price
