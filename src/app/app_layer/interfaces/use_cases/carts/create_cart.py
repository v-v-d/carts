from abc import ABC, abstractmethod

from app.app_layer.interfaces.use_cases.carts.dto import (
    CartCreateByUserIdInputDTO,
    CartOutputDTO,
)


class ICreateCartUseCase(ABC):
    @abstractmethod
    async def create_by_auth_data(self, auth_data: str) -> CartOutputDTO:
        ...

    @abstractmethod
    async def create_by_user_id(self, data: CartCreateByUserIdInputDTO) -> CartOutputDTO:
        ...
