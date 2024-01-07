from logging import getLogger

from app.app_layer.interfaces.auth_system.exceptions import OperationForbiddenError
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.use_cases.carts.dto import CartCreateByUserIdInputDTO, CartOutputDTO
from app.domain.carts.entities import Cart

logger = getLogger(__name__)


class CreateCartUseCase:
    """
    Responsible for creating a new cart for a user. It has two methods:
    create_by_auth_data and create_by_user_id. The first method creates a cart based
    on the authentication data of the user, while the second method creates a cart
    based on the user ID. The class uses an instance of the IUnitOfWork interface to
    interact with the data storage and an instance of the IAuthSystem interface to
    authenticate the user.
    """

    def __init__(
        self,
        uow: IUnitOfWork,
        auth_system: IAuthSystem,
    ) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def create_by_auth_data(self, auth_data: str) -> CartOutputDTO:
        """
        Creates a cart for the user based on their authentication data. It retrieves
        the user data using the get_user_data method of the IAuthSystem interface and
        then creates the cart.
        """

        user = await self._auth_system.get_user_data(auth_data=auth_data)
        return await self._create(user_id=user.id)

    async def create_by_user_id(self, data: CartCreateByUserIdInputDTO) -> CartOutputDTO:
        """
        Creates a cart for the user based on their user ID. It retrieves the user data
        using the get_user_data method of the IAuthSystem interface and then creates
        the cart.
        """

        user = await self._auth_system.get_user_data(auth_data=data.auth_data)

        if not user.is_admin:
            logger.error(
                "Failed to create cart for user %s due to forbidden operation.",
                data.user_id,
            )
            raise OperationForbiddenError

        return await self._create(user_id=data.user_id)

    async def _create(self, user_id: int) -> CartOutputDTO:
        async with self._uow(autocommit=True):
            cart_config = await self._uow.carts.get_config()
            cart = Cart.create(user_id=user_id, config=cart_config)
            await self._uow.carts.create(cart=cart)

        logger.debug("Cart %s successfully created for user %s.", cart.id, cart.user_id)

        return CartOutputDTO.model_validate(cart)
