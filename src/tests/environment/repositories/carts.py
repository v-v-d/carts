from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.domain.carts.entities import Cart
from app.domain.interfaces.repositories.carts.exceptions import (
    ActiveCartAlreadyExistsError,
    CartNotFoundError,
)
from app.infra.repositories.sqla import models
from app.infra.repositories.sqla.carts import CartsRepository


class TestCartsRepository(CartsRepository):
    """
    Test repository for interactions with carts operations through database.
    """

    __test__ = False

    async def get_by_id(self, cart_id: UUID) -> Cart:
        stmt = (
            select(models.Cart)
            .options(joinedload(models.Cart.items))
            .options(joinedload(models.Cart.coupon))
            .where(models.Cart.id == cart_id)
        )
        result = await self._session.scalars(stmt)
        obj = result.first()

        if not obj:
            raise CartNotFoundError

        config = await self._get_config()

        return self._get_cart(obj=obj, config=config)

    async def bulk_create(self, carts: list[Cart], **kwargs) -> list[Cart]:
        stmt = insert(models.Cart).values(
            [
                {
                    "created_at": cart.created_at,
                    "id": cart.id,
                    "user_id": cart.user_id,
                    "status": cart.status,
                    **kwargs,
                }
                for cart in carts
            ]
        )

        try:
            await self._session.execute(stmt)
        except IntegrityError:
            raise ActiveCartAlreadyExistsError

        return carts
