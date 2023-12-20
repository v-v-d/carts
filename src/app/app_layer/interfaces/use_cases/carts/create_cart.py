from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class ICreateCartUseCase(ABC):
    @abstractmethod
    async def execute(self, auth_data: str) -> CartOutputDTO:
        ...
