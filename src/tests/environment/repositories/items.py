from sqlalchemy import insert

from app.domain.items.entities import Item
from app.infra.repositories.sqla import models
from app.infra.repositories.sqla.items import ItemsRepository


class TestItemsRepository(ItemsRepository):
    """
    Test repository for interactions with items operations through database.
    """

    __test__ = False

    async def create_item(self, item: Item) -> None:
        stmt = insert(models.Item).values(
            id=item.id, name=item.name, qty=item.qty, price=item.price
        )
        await self._session.execute(stmt)
