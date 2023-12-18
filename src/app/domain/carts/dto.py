from uuid import UUID

from pydantic import BaseModel


class CartDTO(BaseModel):
    class Config:
        from_attributes = True

    id: UUID
    user_id: int
    is_active: bool
