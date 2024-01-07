from logging import getLogger

from pydantic import ValidationError

from app.app_layer.interfaces.auth_system.dto import UserDataOutputDTO
from app.app_layer.interfaces.auth_system.exceptions import (
    InvalidAuthDataError,
    OperationForbiddenError,
)
from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.logging import update_context

logger = getLogger(__name__)

_USERS_BY_TOKEN = {
    "customer.1": {"id": 1, "roles": ["customer"]},
    "customer.2": {"id": 2, "roles": ["customer"]},
    "admin.1": {"id": 3, "roles": ["admin"]},
}


class FakeJWTAuthSystem(IAuthSystem):
    """
    Provides authentication functionality using a fake JWT token. It validates the
    token, retrieves user data based on the token, and checks if the user is an
    admin.
    """

    def __init__(self) -> None:
        self._token: None | str = None

    def validate_auth_data(self, auth_data: str) -> None:
        """
        Validates the authentication data by checking if it starts with "Bearer " and
        if the token is valid. If the validation fails, it raises an
        InvalidAuthDataError exception.
        """

        if not auth_data.startswith("Bearer "):
            logger.error(
                "Failed to authenticate user with token %s! Error: bad token format.",
                auth_data,
            )
            raise InvalidAuthDataError

        self._token = auth_data.removeprefix("Bearer ")

        if self._token not in _USERS_BY_TOKEN:
            logger.error(
                "Failed to authenticate user with token %s! Error: invalid token.",
                auth_data,
            )
            raise InvalidAuthDataError

    async def get_user_data(self, auth_data: str) -> UserDataOutputDTO:
        """
        Retrieves user data based on the token by looking up the token in the
        _USERS_BY_TOKEN dictionary. If the user data is invalid, it raises an
        InvalidAuthDataError exception. It also updates the context with the user ID.
        """

        self.validate_auth_data(auth_data)

        user_data = _USERS_BY_TOKEN[self._token]

        try:
            user = UserDataOutputDTO(
                id=user_data["id"],
                is_admin="admin" in user_data["roles"],
            )
        except ValidationError as err:
            logger.error(
                "Failed to authenticate user with token %s! Error: %s",
                auth_data,
                str(err),
            )
            raise InvalidAuthDataError

        await update_context(user_id=user.id)
        logger.debug("Got user data %s", user)

        return user

    async def check_for_admin(self, auth_data: str) -> None:
        """
        Checks if the user is an admin by calling the get_user_data method. If the
        user is not an admin, it raises an OperationForbiddenError exception.
        """

        user = await self.get_user_data(auth_data=auth_data)

        if not user.is_admin:
            logger.error("Check for admin failed! Auth data: %s!", auth_data)
            raise OperationForbiddenError
