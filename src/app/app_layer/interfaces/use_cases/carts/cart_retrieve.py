from abc import ABC, abstractmethod
from uuid import UUID

from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class ICartRetrieveUseCase(ABC):
    @abstractmethod
    async def execute(self, cart_id: UUID) -> CartOutputDTO:
        ...
