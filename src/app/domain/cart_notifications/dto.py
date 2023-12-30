from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.cart_notifications.value_objects import CartNotificationTypeEnum


class CartNotificationDTO(BaseModel):
    id: UUID
    cart_id: UUID
    type: CartNotificationTypeEnum
    text: str
    sent_at: datetime
