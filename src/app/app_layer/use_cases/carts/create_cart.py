from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.carts.create_cart import ICreateCartUseCase
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.domain.carts.entities import Cart


class CreateCartUseCase(ICreateCartUseCase):
    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, auth_data: str) -> CartOutputDTO:
        user = self._auth_system.get_user_data(auth_data=auth_data)
        cart = Cart.create(user_id=user.id)

        async with self._uow(autocommit=True):
            await self._uow.carts.create(cart=cart)

        return CartOutputDTO.model_validate(cart)
