from logging import getLogger

from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.repositories.items.exceptions import ItemAlreadyExists
from app.domain.interfaces.repositories.items.repo import IItemsRepository
from app.domain.items.dto import ItemDTO
from app.domain.items.entities import Item
from app.infra.repositories.sqla import models

logger = getLogger(__name__)


class ItemsRepository(IItemsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_item(self, item: Item) -> None:
        stmt = insert(models.CartItem).values(
            id=item.id,
            name=item.name,
            qty=item.qty,
            price=item.price,
            is_weight=item.is_weight,
            cart_id=item.cart_id,
        )

        try:
            await self._session.execute(stmt)
        except IntegrityError as err:
            raise ItemAlreadyExists(str(err)) from err

    async def get_items(self) -> list[Item]:
        stmt = select(models.CartItem)
        result = await self._session.scalars(stmt)

        return [Item(data=ItemDTO.model_validate(item)) for item in result.all()]

    async def update_item(self, item: Item) -> Item:
        stmt = (
            update(models.CartItem)
            .where(models.CartItem.id == item.id, models.CartItem.cart_id == item.cart_id)
            .values(
                name=item.name,
                qty=item.qty,
                price=item.price,
                is_weight=item.is_weight,
            )
        )
        await self._session.execute(stmt)

        return item

    async def delete_item(self, item: Item) -> None:
        stmt = delete(models.CartItem).where(
            models.CartItem.id == item.id, models.CartItem.cart_id == item.cart_id
        )
        await self._session.execute(stmt)
