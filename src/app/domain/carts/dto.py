from uuid import UUID

from pydantic import BaseModel


class CartDTO(BaseModel):
    class Config:
        from_attributes = True

    id: UUID
    is_active: bool
