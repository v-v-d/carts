from uuid import UUID

from app.app_layer.interfaces.services.carts.cart_retrieve import ICartRetrieveService
from app.app_layer.interfaces.services.carts.dto import CartOutputDTO
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork


class CartRetrieveService(ICartRetrieveService):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, cart_id: UUID) -> CartOutputDTO:
        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=cart_id)

        return CartOutputDTO.model_validate(cart)
