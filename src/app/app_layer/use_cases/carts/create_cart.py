from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.cart_items.dto import CreateCartInputDTO
from app.app_layer.interfaces.use_cases.carts.create_cart import ICreateCartUseCase
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO
from app.domain.carts.entities import Cart


class CreateCartUseCase(ICreateCartUseCase):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, data: CreateCartInputDTO) -> CartOutputDTO:
        cart = Cart.create(user_id=data.user_id)

        async with self._uow(autocommit=True):
            await self._uow.carts.create(cart=cart)

        return CartOutputDTO.model_validate(cart)
