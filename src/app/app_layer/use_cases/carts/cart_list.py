from datetime import datetime

from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.use_cases.carts.dto import CartListInputDTO, CartListOutputDTO


class CartListUseCase:
    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, data: CartListInputDTO) -> CartListOutputDTO:
        self._auth_system.check_for_admin(auth_data=data.auth_data)
        created_at = data.created_at or datetime.now()

        async with self._uow(autocommit=True):
            carts = await self._uow.carts.get_list(
                page_size=data.page_size,
                created_at=created_at,
            )

        return CartListOutputDTO.validate_python(carts)
