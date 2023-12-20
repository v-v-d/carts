from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.cart_items.dto import ItemDTO
from app.domain.cart_items.entities import CartItem
from app.domain.carts.dto import CartDTO
from app.domain.carts.entities import Cart
from app.domain.carts.value_objects import CartStatusEnum
from app.domain.interfaces.repositories.carts.exceptions import (
    ActiveCartAlreadyExistsError,
    CartNotFoundError,
)
from app.domain.interfaces.repositories.carts.repo import ICartsRepository
from app.infra.repositories.sqla import models


class CartsRepository(ICartsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, cart: Cart) -> Cart:
        stmt = insert(models.Cart).values(
            id=cart.id,
            user_id=cart.user_id,
            status=cart.status,
        )

        try:
            await self._session.execute(stmt)
        except IntegrityError:
            raise ActiveCartAlreadyExistsError

        return cart

    async def retrieve(self, cart_id: UUID) -> Cart:
        stmt = (
            select(models.Cart)
            .options(joinedload(models.Cart.items))
            .where(
                models.Cart.id == cart_id,
                models.Cart.status != CartStatusEnum.DEACTIVATED,
            )
        )
        result = await self._session.scalars(stmt)
        obj = result.first()

        if not obj:
            raise CartNotFoundError

        return Cart(
            data=CartDTO.model_validate(obj),
            items=[CartItem(data=ItemDTO.model_validate(item)) for item in obj.items],
        )

    async def update(self, cart: Cart) -> Cart:
        stmt = update(models.Cart).where(models.Cart.id == cart.id).values(status=cart.status)
        await self._session.execute(stmt)

        return cart

    async def clear(self, cart_id: UUID) -> None:
        stmt = delete(models.CartItem).where(models.CartItem.cart_id == cart_id)
        await self._session.execute(stmt)
