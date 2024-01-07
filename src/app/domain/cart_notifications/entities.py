from datetime import datetime
from uuid import UUID, uuid4

from app.domain.cart_notifications.dto import CartNotificationDTO
from app.domain.cart_notifications.value_objects import CartNotificationTypeEnum


class CartNotification:
    """
    Represents a notification of a cart. It also provides methods for creating
    different types of cart notifications.
    """

    def __init__(self, data: CartNotificationDTO) -> None:
        self.id = data.id
        self.cart_id = data.cart_id
        self.type = data.type
        self.text = data.text
        self.sent_at = data.sent_at

    @classmethod
    def create(
        cls,
        cart_id: UUID,
        notification_type: CartNotificationTypeEnum,
        text: str,
    ) -> "CartNotification":
        """
        Creates a cart notification with the given cart ID, notification type, and
        text.
        """

        return cls(
            data=CartNotificationDTO(
                id=uuid4(),
                cart_id=cart_id,
                type=notification_type,
                text=text,
                sent_at=datetime.now(),
            ),
        )

    @classmethod
    def create_abandoned_cart_notification(
        cls, cart_id: UUID, text: str
    ) -> "CartNotification":
        """
        Creates an abandoned cart notification with the given cart ID and text.
        """

        return cls.create(
            cart_id=cart_id,
            notification_type=CartNotificationTypeEnum.ABANDONED_CART,
            text=text,
        )
