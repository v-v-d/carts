from abc import ABC, abstractmethod

from app.interfaces.clients.products.dto import ProductOutputDTO


class IProductsClient(ABC):
    @abstractmethod
    async def get_product(self, item_id: int) -> ProductOutputDTO:
        ...
