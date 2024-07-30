from logging import getLogger

from sqlalchemy import delete, update, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.domain.interfaces.repositories.items.exceptions import ItemAlreadyExists
from app.domain.interfaces.repositories.items.repo import IItemsRepository
from app.infra.repositories.sqla import models

logger = getLogger(__name__)


class ItemsRepository(IItemsRepository):
    """
    Responsible for interacting with the database to perform CRUD operations on
    CartItem objects. It uses SQLAlchemy to execute SQL statements asynchronously.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_item(self, item: CartItem) -> None:
        """Inserts a new CartItem object into the database."""

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

        stmt = text(
            """
            PREPARE cypher_stored_procedure(agtype) AS
            SELECT *
            FROM cypher(
                'template',
                $$
                    MATCH (c:Cart) WHERE c.id = $cart_id
                    MERGE (i:CartItem {id: $item_id})
                    MERGE (c)-[r:CONTAINS]->(i)
                    RETURN i
                $$,
                $1
            ) as (i agtype);
            """
        )
        await self._session.execute(stmt, params={"cart_id": item.cart_id, "item_id": item.id})
        await self._session.execute(text("DEALLOCATE cypher_stored_procedure;"))

    async def update_item(self, item: CartItem) -> CartItem:
        """Updates an existing CartItem object in the database."""

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

    async def delete_item(self, cart: Cart, item_id: int) -> None:
        """
        Deletes an item from the database based on the provided cart and item_id.
        """

        stmt = delete(models.CartItem).where(
            models.CartItem.id == item_id, models.CartItem.cart_id == cart.id
        )
        await self._session.execute(stmt)

        stmt = text(
            """
            PREPARE cypher_stored_procedure(agtype) AS
            SELECT *
            FROM cypher(
                'template', 
                $$
                    MATCH (c:Cart)-[r:CONTAINS]->(i:CartItem) 
                    WHERE c.id = $cart_id AND i.id = $item_id
                    DELETE r
                $$, 
                $1, $2
            ) as (n agtype);
            """
        )
        await self._session.execute(stmt, params={"cart_id": cart.id, "item_id": item_id})
