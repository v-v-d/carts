from datetime import datetime

from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.use_cases.carts.dto import CartListInputDTO, CartListOutputDTO


class CartListUseCase:
    """
    Responsible for retrieving a list of carts based on certain criteria. It uses an
    instance of the IUnitOfWork interface to interact with the data storage and the
    IAuthSystem interface to validate the authentication data.
    """

    def __init__(self, uow: IUnitOfWork, auth_system: IAuthSystem) -> None:
        self._uow = uow
        self._auth_system = auth_system

    async def execute(self, data: CartListInputDTO) -> CartListOutputDTO:
        """
        Executes the use case by validating the authentication data, retrieving the
        list of carts based on the provided criteria, and returning the list of carts
        as an instance of the CartListOutputDTO class.
        """

        await self._auth_system.check_for_admin(auth_data=data.auth_data)
        created_at = data.created_at or datetime.now()

        async with self._uow(autocommit=True):
            carts = await self._uow.carts.get_list(
                page_size=data.page_size,
                created_at=created_at,
            )

        return CartListOutputDTO.validate_python(carts)
