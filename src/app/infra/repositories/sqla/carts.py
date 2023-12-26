import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import Row, delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.cart_config.dto import CartConfigDTO
from app.domain.cart_config.entities import CartConfig
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

        config = await self._get_config()

        return self._get_cart(obj=obj, config=config)

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

        config = await self._get_config()

        return [self._get_cart(obj=obj, config=config) for obj in objects]

    async def get_config(self) -> CartConfig:
        return await self._get_config()

    async def update_config(self, cart_config: CartConfig) -> CartConfig:
        stmt = delete(models.CartConfig)
        await self._session.execute(stmt)

        value_by_name = [
            {"name": name, "value": json.dumps(value, default=lambda x: str(x))}
            for name, value in cart_config.data.model_dump().items()
        ]

        stmt = insert(models.CartConfig).values(value_by_name)
        await self._session.execute(stmt)

        return cart_config

    async def _get_config(self) -> CartConfig:
        stmt = select(models.CartConfig)
        result = await self._session.scalars(stmt)

        rows = result.unique().all()
        value_by_name = {row.name: json.loads(row.value) for row in rows}

        return CartConfig(data=CartConfigDTO.model_validate(value_by_name))

    def _get_cart(self, obj: Row, config: CartConfig) -> Cart:
        cart = Cart(
            data=CartDTO.model_validate(obj),
            items=[CartItem(data=ItemDTO.model_validate(item)) for item in obj.items],
            config=config,
        )

        if obj.coupon is None:
            return cart

        cart.coupon = CartCoupon(data=CartCouponDTO.model_validate(obj.coupon), cart=cart)

        return cart
