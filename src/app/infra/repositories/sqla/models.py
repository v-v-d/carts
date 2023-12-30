from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column, relationship

from app.domain.cart_coupons.value_objects import (
    CART_COST_PRECISION,
    CART_COST_SCALE,
    DISCOUNT_PRECISION,
    DISCOUNT_SCALE,
    CartCost,
    Discount,
)
from app.domain.cart_items.value_objects import ITEM_PRICE_PRECISION, ITEM_PRICE_SCALE
from app.domain.cart_notifications.value_objects import CartNotificationTypeEnum
from app.domain.carts.value_objects import CartStatusEnum
from app.infra.repositories.sqla.base import Base


@declarative_mixin
class TimestampMixin:
    timestamp = Annotated[
        datetime,
        mapped_column(
            nullable=False,
            default=datetime.utcnow,
            server_default=func.CURRENT_TIMESTAMP(),
        ),
    ]

    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp] = mapped_column(
        onupdate=datetime.utcnow,
        server_onupdate=func.CURRENT_TIMESTAMP(),
    )


class CartItem(TimestampMixin, Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    cart_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey(column="carts.id", name="item_cart_id_fkey", ondelete="CASCADE"),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    qty: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(
        sa.Numeric(precision=ITEM_PRICE_PRECISION, scale=ITEM_PRICE_SCALE),
        nullable=False,
    )
    is_weight: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)

    cart: Mapped["Cart"] = relationship(
        "Cart", lazy="noload", back_populates="items", uselist=False
    )


class Cart(TimestampMixin, Base):
    __tablename__ = "carts"

    id: Mapped[UUID] = mapped_column(
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
    coupon: Mapped["CartCoupon"] = relationship(
        "CartCoupon", lazy="noload", uselist=False
    )

    __table_args__ = (
        Index(
            "idx_user_id_opened_status_unique",
            "user_id",
            "status",
            unique=True,
            postgresql_where=(
                status.in_([CartStatusEnum.OPENED.value, CartStatusEnum.LOCKED.value])
            ),
        ),
    )


class CartCoupon(TimestampMixin, Base):
    __tablename__ = "carts_coupons"

    cart_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey(
            column="carts.id", name="cart_coupon_cart_id_fkey", ondelete="CASCADE"
        ),
        primary_key=True,
    )
    coupon_id: Mapped[str] = mapped_column(sa.Text, nullable=False)
    min_cart_cost: Mapped[CartCost] = mapped_column(
        sa.Numeric(precision=CART_COST_PRECISION, scale=CART_COST_SCALE),
        nullable=False,
    )
    discount_abs: Mapped[Discount] = mapped_column(
        sa.Numeric(precision=DISCOUNT_PRECISION, scale=DISCOUNT_SCALE),
        nullable=False,
    )


class CartConfig(TimestampMixin, Base):
    __tablename__ = "cart_config"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)


class CartNotification(TimestampMixin, Base):
    __tablename__ = "cart_notifications"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    cart_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey(
            column="carts.id",
            name="cart_notifications_cart_id_fkey",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )
    type: Mapped[CartNotificationTypeEnum] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(nullable=False)
