from abc import ABC, abstractmethod
from uuid import UUID

from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class ICartDeleteUseCase(ABC):
    @abstractmethod
    async def execute(self, auth_data: str, cart_id: UUID) -> CartOutputDTO:
        ...
