from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.interfaces.repositories.items import IItemsRepository
from domain.items.dto import ItemDTO
from domain.items.entities import Item
from infra.repositories.alchemy import models


class ItemsRepository(IItemsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_item(self, item: Item) -> None:
        stmt = insert(models.Item).values(
            id=item.id,
            name=item.name,
            qty=item.qty,
            price=item.price,
        )

        await self._session.execute(stmt)

    async def get_items(self) -> list[Item]:
        stmt = select(models.Item)
        result = await self._session.scalars(stmt)

        return [Item(data=ItemDTO.model_validate(item)) for item in result.all()]
