from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.carts.value_objects import CartStatusEnum


class CartDTO(BaseModel):
    class Config:
        from_attributes = True

    created_at: datetime
    id: UUID
    user_id: int
    status: CartStatusEnum
