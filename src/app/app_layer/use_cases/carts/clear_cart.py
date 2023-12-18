from uuid import UUID

from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.carts.clear_cart import IClearCartUseCase
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class ClearCartUseCase(IClearCartUseCase):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, cart_id: UUID) -> CartOutputDTO:
        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=cart_id)
            cart.clear()
            await self._uow.carts.clear(cart_id=cart.id)

        return CartOutputDTO.model_validate(cart)
