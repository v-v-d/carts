from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.cart_items import entities
from app.domain.carts.value_objects import CartStatusEnum
from app.infra.repositories.sqla.base import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    cart_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey(column="carts.id", name="item_cart_id_fkey", ondelete="CASCADE"),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    qty: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(
        sa.Numeric(entities.CartItem.price_precision, entities.CartItem.price_scale),
        nullable=False,
    )
    is_weight: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)

    cart: Mapped["Cart"] = relationship(
        "Cart", lazy="noload", back_populates="items", uselist=False
    )


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    status: Mapped[CartStatusEnum] = mapped_column(
        default=CartStatusEnum.OPENED,
        server_default=CartStatusEnum.OPENED,
    )

    items: Mapped[list[CartItem]] = relationship(
        "CartItem", lazy="noload", back_populates="cart"
    )

    __table_args__ = (
        Index(
            "idx_user_id_opened_status_unique",
            "user_id",
            "status",
            unique=True,
            postgresql_where=(status.__eq__(CartStatusEnum.OPENED.value)),
        ),
    )
