import pytest

from app.app_layer.interfaces.use_cases.items.items_list import IItemsListUseCase
from app.app_layer.use_cases.items.items_list import ItemsListUseCase
from app.domain.items.entities import Item
from tests.environment.unit_of_work import TestUow


@pytest.fixture()
def use_case(uow: TestUow) -> IItemsListUseCase:
    return ItemsListUseCase(uow=uow)


async def test_ok(use_case: IItemsListUseCase, existing_item: Item) -> None:
    result = await use_case.execute()

    assert len(result) == 1
    assert result[0].id == existing_item.id
    assert result[0].qty == existing_item.qty
    assert result[0].name == existing_item.name
    assert result[0].price == existing_item.price
