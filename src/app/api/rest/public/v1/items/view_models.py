from pydantic import BaseModel, Field


class BaseItemViewModel(BaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True

    id: int
    name: str = Field(alias="title")
    qty: float = Field(alias="quantity")
    price: float
    cost: float


class ItemAddingViewModel(BaseItemViewModel):
    pass


class ItemListViewModel(BaseItemViewModel):
    pass
