from datetime import datetime
from logging import getLogger
from uuid import UUID

from sqlalchemy import Row, delete, func, select, text, update
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
from app.domain.cart_notifications.value_objects import CartNotificationTypeEnum
from app.domain.carts.dto import CartDTO
from app.domain.carts.entities import Cart
from app.domain.carts.value_objects import CartStatusEnum
from app.domain.interfaces.repositories.carts.exceptions import (
    ActiveCartAlreadyExistsError,
    CartNotFoundError,
)
from app.domain.interfaces.repositories.carts.repo import ICartsRepository
from app.infra.repositories.sqla import models
from app.logging import update_context

logger = getLogger(__name__)


class CartsRepository(ICartsRepository):
    """
    Responsible for interacting with the database to perform CRUD operations on the
    Cart objects. It provides methods to create a new cart, retrieve an existing
    cart, update a cart's status, clear a cart's items, get a list of carts, get the
    cart configuration, update the cart configuration, and find abandoned carts based
    on certain criteria.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, cart: Cart) -> Cart:
        """
        Creates a new cart in the database and returns the created cart object.
        """

        stmt = insert(models.Cart).values(
            created_at=cart.created_at,
            id=cart.id,
            user_id=cart.user_id,
            status=cart.status,
        )

        try:
            await self._session.execute(stmt)
        except IntegrityError:
            raise ActiveCartAlreadyExistsError

        stmt = text(
            """
            PREPARE cypher_stored_procedure(agtype) AS
            SELECT *
            FROM cypher(
                'template', 
                $$
                    MERGE (n:Cart {id: $cart_id})
                $$, 
                $1
            ) as (n agtype);
            """
        )
        await self._session.execute(stmt, params={"cart_id": cart.id})
        await self._session.execute(text("DEALLOCATE cypher_stored_procedure;"))

        await update_context(cart_id=cart.id)

        return cart

    async def retrieve(self, cart_id: UUID) -> Cart:
        """
        Retrieves an existing cart from the database based on the provided cart ID
        and returns the retrieved cart object.
        """

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
        cart = self._get_cart(obj=obj, config=config)

        logger.debug("Got cart: %s", vars(cart))

        return cart

    async def update(self, cart: Cart) -> Cart:
        """
        Updates the status of a cart in the database based on the provided cart
        object and returns the updated cart object.
        """

        stmt = (
            update(models.Cart)
            .where(models.Cart.id == cart.id)
            .values(status=cart.status)
        )
        await self._session.execute(stmt)

        return cart

    async def clear(self, cart_id: UUID) -> None:
        """
        Clears the items of a cart in the database based on the provided cart ID.
        """

        stmt = delete(models.CartItem).where(models.CartItem.cart_id == cart_id)
        await self._session.execute(stmt)

    async def get_list(self, page_size: int, created_at: datetime) -> list[Cart]:
        """
        Retrieves a list of carts from the database based on the specified page
        size and creation date and returns a list of cart objects.
        """

        stmt = (
            select(models.Cart)
            .options(joinedload(models.Cart.items))
            .options(joinedload(models.Cart.coupon))
            .where(models.Cart.created_at < created_at)
            .order_by(models.Cart.created_at.desc())
            .limit(page_size)
        )
        result = await self._session.scalars(stmt)
        objects = result.unique().all()

        config = await self._get_config()

        return [self._get_cart(obj=obj, config=config) for obj in objects]

    async def get_config(self) -> CartConfig:
        """
        Retrieves the cart configuration from the database and returns the cart
        configuration object.
        """

        return await self._get_config()

    async def update_config(self, cart_config: CartConfig) -> CartConfig:
        """
        Updates the cart configuration in the database based on the provided cart
        configuration object and returns the updated cart configuration object.
        """

        stmt = update(models.CartConfig).values(data=vars(cart_config))
        await self._session.execute(stmt)

        return cart_config

    async def find_abandoned_cart_id_by_user_id(self) -> list[tuple[int, UUID]]:
        """
        Finds abandoned carts in the database based on certain criteria and returns
        a list of tuples containing the user ID and cart ID of the abandoned carts.
        """

        config = await self._get_config()
        abandonment_threshold_time = func.now() - text(
            f"INTERVAL '{config.hours_since_update_until_abandoned} hours'"
        )

        subquery = (
            select(
                models.CartNotification.cart_id,
                func.count().label("notifications_count"),
            )
            .join(models.Cart, models.CartNotification.cart_id == models.Cart.id)
            .where(
                models.Cart.updated_at <= abandonment_threshold_time,
                models.Cart.status == CartStatusEnum.OPENED,
                models.CartNotification.type == CartNotificationTypeEnum.ABANDONED_CART,
            )
            .group_by(models.CartNotification.cart_id)
        ).subquery()

        stmt = (
            select(models.Cart.user_id, models.Cart.id)
            .outerjoin(subquery, models.Cart.id == subquery.c.cart_id)
            .where(
                models.Cart.updated_at <= abandonment_threshold_time,
                models.Cart.status == CartStatusEnum.OPENED,
                (subquery.c.notifications_count.is_(None))
                | (
                    subquery.c.notifications_count
                    < config.max_abandoned_notifications_qty
                ),
            )
        )

        result = await self._session.execute(stmt)

        return [(user_id, cart_id) for user_id, cart_id in result.all()]

    async def _get_config(self) -> CartConfig:
        stmt = select(models.CartConfig)
        row = await self._session.scalar(stmt)

        return CartConfig(data=CartConfigDTO.model_validate(row.data))

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
