from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from app.domain.cart_notifications.dto import CartNotificationDTO
from app.domain.cart_notifications.entities import CartNotification
from app.domain.interfaces.repositories.carts.exceptions import (
    ActiveCartAlreadyExistsError,
)
from app.infra.repositories.sqla import models
from app.infra.repositories.sqla.cart_notifications import CartsNotificationsRepository


class TestCartsNotificationsRepository(CartsNotificationsRepository):
    """
    Test repository for interactions with carts notifications operations through database.
    """

    __test__ = False

    async def bulk_create(
        self,
        notifications: list[CartNotification],
    ) -> list[CartNotification]:
        stmt = insert(models.CartNotification).values(
            [
                {
                    "id": notification.id,
                    "cart_id": notification.cart_id,
                    "type": notification.type,
                    "text": notification.text,
                    "sent_at": notification.sent_at,
                }
                for notification in notifications
            ]
        )

        try:
            await self._session.execute(stmt)
        except IntegrityError:
            raise ActiveCartAlreadyExistsError

        return notifications

    async def retrieve(self, cart_id: UUID) -> CartNotification | None:
        stmt = select(models.CartNotification).where(
            models.CartNotification.cart_id == cart_id
        )
        row = await self._session.scalar(stmt)

        if not row:
            return

        return CartNotification(
            data=CartNotificationDTO(
                id=row.id,
                cart_id=row.cart_id,
                type=row.type,
                text=row.text,
                sent_at=row.sent_at,
            ),
        )
