from uuid import UUID

from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.carts.cart_delete import ICartDeleteUseCase
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class CartDeleteUseCase(ICartDeleteUseCase):
    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, auth_data: str, cart_id: UUID) -> CartOutputDTO:
        user = self._auth_system.get_user_data(auth_data=auth_data)

        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(user_id=user.id, cart_id=cart_id)
            cart.deactivate()
            await self._uow.carts.update(user_id=user.id, cart=cart)

        return CartOutputDTO.model_validate(cart)
