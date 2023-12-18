from sqlalchemy import insert

from app.domain.cart_items.entities import CartItem
from app.infra.repositories.sqla import models
from app.infra.repositories.sqla.items import ItemsRepository


class TestItemsRepository(ItemsRepository):
    """
    Test repository for interactions with cart_items operations through database.
    """

    __test__ = False

    async def create_item(self, item: CartItem) -> None:
        stmt = insert(models.CartItem).values(
            id=item.id, name=item.name, qty=item.qty, price=item.price
        )
        await self._session.execute(stmt)
