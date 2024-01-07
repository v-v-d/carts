from logging import getLogger

from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.use_cases.cart_config.dto import (
    CartConfigInputDTO,
    CartConfigOutputDTO,
)
from app.domain.cart_config.dto import CartConfigDTO
from app.domain.cart_config.entities import CartConfig

logger = getLogger(__name__)


class CartConfigService:
    """
    Responsible for retrieving and updating the cart configuration. It interacts with
    the IUnitOfWork and IAuthSystem interfaces to access the necessary data and perform
    authentication.
    """

    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def retrieve(self, auth_data: str) -> CartConfigOutputDTO:
        """
        Retrieves the cart configuration by validating the authentication data and
        calling the get_config method of the carts repository.
        """

        await self._auth_system.check_for_admin(auth_data=auth_data)

        async with self._uow(autocommit=True):
            result = await self._uow.carts.get_config()

        return CartConfigOutputDTO.model_validate(result)

    async def update(self, data: CartConfigInputDTO) -> CartConfigOutputDTO:
        """
        Updates the cart configuration by validating the authentication data, creating
        a CartConfig instance with the input data, and calling the update_config method
        of the carts repository.
        """

        await self._auth_system.check_for_admin(auth_data=data.auth_data)

        cart_config = CartConfig(
            data=CartConfigDTO(
                max_items_qty=data.max_items_qty,
                min_cost_for_checkout=data.min_cost_for_checkout,
                limit_items_by_id=data.limit_items_by_id,
                hours_since_update_until_abandoned=data.hours_since_update_until_abandoned,
                max_abandoned_notifications_qty=data.max_abandoned_notifications_qty,
                abandoned_cart_text=data.abandoned_cart_text,
            )
        )

        async with self._uow(autocommit=True):
            result = await self._uow.carts.update_config(cart_config=cart_config)

        logger.info("Cart config successfully updated!")

        return CartConfigOutputDTO.model_validate(result)
