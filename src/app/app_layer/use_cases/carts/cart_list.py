from pydantic import TypeAdapter

from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.carts.cart_list import ICartListUseCase
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class CartListUseCase(ICartListUseCase):
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def execute(self) -> list[CartOutputDTO]:
        async with self._uow(autocommit=True):
            carts = await self._uow.carts.get_list()

        return TypeAdapter(list[CartOutputDTO]).validate_python(carts)
