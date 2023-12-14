from abc import ABC, abstractmethod
from uuid import UUID

from app.app_layer.interfaces.services.carts.dto import CartOutputDTO


class ICartRetrieveService(ABC):
    @abstractmethod
    async def execute(self, cart_id: UUID) -> CartOutputDTO:
        ...
