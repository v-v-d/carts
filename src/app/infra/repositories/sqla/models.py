from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.items import entities
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
        sa.Numeric(entities.Item.price_precision, entities.Item.price_scale),
        nullable=False,
    )
    is_weight: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)

    cart: Mapped["Cart"] = relationship(
        "Cart", lazy="noload", back_populates="items", uselist=False
    )


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)

    items: Mapped[list[CartItem]] = relationship("CartItem", lazy="noload", back_populates="cart")

    __table_args__ = (
        Index(
            "idx_user_id_is_active_unique",
            "user_id",
            "is_active",
            unique=True,
            postgresql_where=(is_active.is_(True)),
        ),
    )
