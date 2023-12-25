from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update, Row
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import CartConfig
from app.domain.cart_coupons.dto import CartCouponDTO
from app.domain.cart_coupons.entities import CartCoupon
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
    def __init__(self, session: AsyncSession, config: CartConfig) -> None:
        self._session = session
        self._config = config

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
            .options(joinedload(models.Cart.coupon))
            .where(
                models.Cart.id == cart_id,
                models.Cart.status != CartStatusEnum.DEACTIVATED,
            )
        )
        result = await self._session.scalars(stmt)
        obj = result.first()

        if not obj:
            raise CartNotFoundError

        return self._get_cart(obj=obj)

    async def update(self, cart: Cart) -> Cart:
        stmt = (
            update(models.Cart)
            .where(models.Cart.id == cart.id)
            .values(status=cart.status)
        )
        await self._session.execute(stmt)

        return cart

    async def clear(self, cart_id: UUID) -> None:
        stmt = delete(models.CartItem).where(models.CartItem.cart_id == cart_id)
        await self._session.execute(stmt)

    async def get_list(self, page_size: int, created_at: datetime) -> list[Cart]:
        stmt = (
            select(models.Cart)
            .options(joinedload(models.Cart.items))
            .options(joinedload(models.Cart.coupon))
            .where(models.Cart.created_at >= created_at)
            .order_by(models.Cart.created_at.desc())
            .limit(page_size)
        )
        result = await self._session.scalars(stmt)
        objects = result.unique().all()

        return [self._get_cart(obj=obj) for obj in objects]

    def _get_cart(self, obj: Row) -> Cart:
        cart = Cart(
            data=CartDTO.model_validate(obj),
            items=[CartItem(data=ItemDTO.model_validate(item)) for item in obj.items],
            config=self._config,
        )

        if obj.coupon is None:
            return cart

        cart.coupon = CartCoupon(data=CartCouponDTO.model_validate(obj.coupon), cart=cart)

        return cart
