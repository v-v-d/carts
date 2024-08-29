from app.app_layer.interfaces.auth_system.dto import UserDataOutputDTO
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.use_cases.carts.dto import CartOutputDTO
from app.domain.carts.entities import Cart


class CartActiveRetrieveUseCase:
    """
    Responsible for retrieving an active cart and validating the user's ownership of the cart.
    """

    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, auth_data: str) -> CartOutputDTO:
        """
        Executes the use case by retrieving the cart and validating the user's
        ownership. Returns the retrieved cart as a CartOutputDTO object.
        """

        user = await self._auth_system.get_user_data(auth_data=auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve_active()

        self._check_user_ownership(cart=cart, user=user)

        return CartOutputDTO.model_validate(cart)

    def _check_user_ownership(self, cart: Cart, user: UserDataOutputDTO) -> None:
        if user.is_admin:
            return

        cart.check_user_ownership(user_id=user.id)
