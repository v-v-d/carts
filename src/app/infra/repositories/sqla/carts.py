from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.carts.dto import CartDTO
from app.domain.carts.entities import Cart
from app.domain.interfaces.repositories.carts.exceptions import (
    CartNotFoundError,
    ActiveCartAlreadyExistsError,
)
from app.domain.interfaces.repositories.carts.repo import ICartsRepository
from app.domain.items.dto import ItemDTO
from app.domain.items.entities import Item
from app.infra.repositories.sqla import models


class CartsRepository(ICartsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, cart: Cart) -> Cart:
        stmt = insert(models.Cart).values(
            id=cart.id,
            user_id=cart.user_id,
            is_active=cart.is_active,
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
                models.Cart.is_active.is_(True),
            )
        )
        result = await self._session.scalars(stmt)
        obj = result.first()

        if not obj:
            raise CartNotFoundError

        return Cart(
            data=CartDTO.model_validate(obj),
            items=[Item(data=ItemDTO.model_validate(item)) for item in obj.items],
        )

    async def update(self, cart: Cart) -> Cart:
        stmt = update(models.Cart).where(models.Cart.id == cart.id).values(is_active=cart.is_active)
        await self._session.execute(stmt)

        return cart

    async def get_list(self) -> list[Cart]:
        stmt = (
            select(models.Cart)
            .options(joinedload(models.Cart.items))
            .where(
                models.Cart.is_active.is_(True),
            )
        )
        result = await self._session.scalars(stmt)
        obj_list = result.unique().all()

        return [
            Cart(
                data=CartDTO.model_validate(obj),
                items=[Item(data=ItemDTO.model_validate(item)) for item in obj.items],
            )
            for obj in obj_list
        ]

    async def clear(self, cart_id: UUID) -> None:
        stmt = delete(models.CartItem).where(models.CartItem.cart_id == cart_id)
        await self._session.execute(stmt)
