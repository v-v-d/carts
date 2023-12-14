from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.carts.entities import Cart
from app.domain.interfaces.repositories.carts.exceptions import CartNotFoundError
from app.domain.interfaces.repositories.carts.repo import ICartsRepository
from app.domain.items.dto import ItemDTO
from app.domain.items.entities import Item
from app.infra.repositories.sqla import models


class CartsRepository(ICartsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def retrieve(self, cart_id: UUID) -> Cart:
        stmt = (
            select(models.Cart)
            .options(joinedload(models.Cart.items))
            .where(models.Cart.id == cart_id)
        )
        result = await self._session.scalars(stmt)
        obj = result.first()

        if not obj:
            raise CartNotFoundError

        return Cart(
            cart_id=obj.id,
            items=[Item(data=ItemDTO.model_validate(item)) for item in obj.items],
        )
