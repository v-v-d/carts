from sqlalchemy import Enum, MetaData
from sqlalchemy.orm import DeclarativeBase

from app.config import Config
from app.domain.carts.value_objects import CartStatusEnum

config = Config()

metadata = MetaData(schema=config.DB.schema_name)


class Base(DeclarativeBase):
    metadata = metadata

    type_annotation_map = {
        CartStatusEnum: Enum(CartStatusEnum, name="cart_status_enum"),
    }
