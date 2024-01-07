from app.app_layer.interfaces.auth_system.dto import UserDataOutputDTO
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.use_cases.carts.dto import CartOutputDTO, CartRetrieveInputDTO
from app.domain.carts.entities import Cart
from app.logging import update_context


class CartRetrieveUseCase:
    """
    Responsible for retrieving a cart and validating the user's ownership of the cart.
    """

    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, data: CartRetrieveInputDTO) -> CartOutputDTO:
        """
        Executes the use case by retrieving the cart and validating the user's
        ownership. Returns the retrieved cart as a CartOutputDTO object.
        """

        await update_context(cart_id=data.cart_id)

        user = await self._auth_system.get_user_data(auth_data=data.auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=data.cart_id)

        self._check_user_ownership(cart=cart, user=user)

        return CartOutputDTO.model_validate(cart)

    def _check_user_ownership(self, cart: Cart, user: UserDataOutputDTO) -> None:
        if user.is_admin:
            return

        cart.check_user_ownership(user_id=user.id)
