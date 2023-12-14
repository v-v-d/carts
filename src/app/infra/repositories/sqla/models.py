from decimal import Decimal
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.items import entities
from app.infra.repositories.sqla.base import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    qty: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(
        sa.Numeric(entities.Item.price_precision, entities.Item.price_scale),
        nullable=False,
    )
    is_weight: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    cart_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("carts.id", name="item_cart_id_fkey", ondelete="CASCADE"),
    )

    cart: Mapped["Cart"] = relationship(
        "Cart", lazy="noload", back_populates="items", uselist=False
    )


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)

    items: Mapped[list[Item]] = relationship("Item", lazy="noload", back_populates="cart")
