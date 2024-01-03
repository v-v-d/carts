from logging import getLogger

from pydantic import ValidationError

from app.app_layer.interfaces.auth_system.dto import UserDataOutputDTO
from app.app_layer.interfaces.auth_system.exceptions import (
    InvalidAuthDataError,
    OperationForbiddenError,
)
from app.app_layer.interfaces.auth_system.system import IAuthSystem

logger = getLogger(__name__)

_USERS_BY_TOKEN = {
    "customer.1": {"id": 1, "roles": ["customer"]},
    "customer.2": {"id": 2, "roles": ["customer"]},
    "admin.1": {"id": 5, "roles": ["admin"]},
}


class FakeJWTAuthSystem(IAuthSystem):
    def __init__(self) -> None:
        self._token: None | str = None

    def validate_auth_data(self, auth_data: str) -> None:
        if not auth_data.startswith("Bearer "):
            raise InvalidAuthDataError

        self._token = auth_data.removeprefix("Bearer ")

        if self._token not in _USERS_BY_TOKEN:
            raise InvalidAuthDataError

    def get_user_data(self, auth_data: str) -> UserDataOutputDTO:
        self.validate_auth_data(auth_data)

        user_data = _USERS_BY_TOKEN[self._token]

        try:
            return UserDataOutputDTO(
                id=user_data["id"],
                is_admin="admin" in user_data["roles"],
            )
        except ValidationError as err:
            logger.info(
                "Failed to authenticate user with token %s! Error: %s",
                auth_data,
                str(err),
            )
            raise InvalidAuthDataError

    def check_for_admin(self, auth_data: str) -> None:
        user = self.get_user_data(auth_data=auth_data)

        if not user.is_admin:
            logger.info("Check for admin failed! Auth data: %s!", auth_data)
            raise OperationForbiddenError
