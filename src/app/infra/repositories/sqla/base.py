from sqlalchemy import Enum, MetaData
from sqlalchemy.orm import DeclarativeBase

from app.config import Config
from app.domain.cart_notifications.value_objects import CartNotificationTypeEnum
from app.domain.carts.value_objects import CartStatusEnum

config = Config()

metadata = MetaData(schema=config.DB.schema_name)


class Base(DeclarativeBase):
    metadata = metadata

    type_annotation_map = {
        CartStatusEnum: Enum(CartStatusEnum, name="cart_status_enum"),
        CartNotificationTypeEnum: Enum(
            CartNotificationTypeEnum, name="cart_notification_type_enum"
        ),
    }
