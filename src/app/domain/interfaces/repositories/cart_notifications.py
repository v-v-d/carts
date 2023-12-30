from abc import ABC, abstractmethod

from app.domain.cart_notifications.entities import CartNotification


class ICartNotificationsRepository(ABC):
    @abstractmethod
    async def create(self, cart_notification: CartNotification) -> CartNotification:
        ...
