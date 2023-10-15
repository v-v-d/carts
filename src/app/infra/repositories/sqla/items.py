from logging import getLogger

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.app_layer.interfaces.repositories.items.exceptions import ItemAlreadyExists
from app.app_layer.interfaces.repositories.items.repo import IItemsRepository
from app.domain.items.dto import ItemDTO
from app.domain.items.entities import Item
from app.infra.repositories.sqla import models

logger = getLogger(__name__)


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

        try:
            await self._session.execute(stmt)
        except IntegrityError as err:
            raise ItemAlreadyExists(str(err)) from err

    async def get_items(self) -> list[Item]:
        stmt = select(models.Item)
        result = await self._session.scalars(stmt)

        return [Item(data=ItemDTO.model_validate(item)) for item in result.all()]
