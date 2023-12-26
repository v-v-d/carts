from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.cart_config.dto import (
    CartConfigInputDTO,
    CartConfigOutputDTO,
)


class ICartConfigService(ABC):
    @abstractmethod
    async def retrieve(self, auth_data: str) -> CartConfigOutputDTO:
        ...

    @abstractmethod
    async def update(self, data: CartConfigInputDTO) -> CartConfigOutputDTO:
        ...
