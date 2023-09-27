from decimal import Decimal

from pydantic import BaseModel, AnyHttpUrl


class RatingOutputDTO(BaseModel):
    rate: float
    count: int


class ProductOutputDTO(BaseModel):
    id: int
    title: str
    price: Decimal
    description: str
    category: str
    image: AnyHttpUrl
    rating: RatingOutputDTO
