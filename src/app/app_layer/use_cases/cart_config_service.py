from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.cart_config.dto import (
    CartConfigInputDTO,
    CartConfigOutputDTO,
)
from app.app_layer.interfaces.use_cases.cart_config.service import ICartConfigService
from app.domain.cart_config.dto import CartConfigDTO
from app.domain.cart_config.entities import CartConfig


class CartConfigService(ICartConfigService):
    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def retrieve(self, auth_data: str) -> CartConfigOutputDTO:
        self._auth_system.check_for_admin(auth_data=auth_data)

        async with self._uow(autocommit=True):
            result = await self._uow.carts.get_config()

        return CartConfigOutputDTO.model_validate(result)

    async def update(self, data: CartConfigInputDTO) -> CartConfigOutputDTO:
        self._auth_system.check_for_admin(auth_data=data.auth_data)

        cart_config = CartConfig(
            data=CartConfigDTO(
                max_items_qty=data.max_items_qty,
                min_cost_for_checkout=data.min_cost_for_checkout,
                limit_items_by_id=data.limit_items_by_id,
            )
        )

        async with self._uow(autocommit=True):
            result = await self._uow.carts.update_config(cart_config=cart_config)

        return CartConfigOutputDTO.model_validate(result)
