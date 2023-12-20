from pydantic import ValidationError

from app.app_layer.interfaces.auth_system.dto import UserDataOutputDTO
from app.app_layer.interfaces.auth_system.exceptions import InvalidAuthDataError
from app.app_layer.interfaces.auth_system.system import IAuthSystem

_USERS_BY_TOKEN = {
    "Bearer fa.ke.1": {"id": 1},
    "Bearer fa.ke.2": {"id": 2},
    "Bearer fa.ke.3": {"id": 3},
    "Bearer fa.ke.4": {"id": 4},
    "Bearer fa.ke.5": {"id": 5},
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

        try:
            return UserDataOutputDTO(**_USERS_BY_TOKEN[self._token])
        except ValidationError:
            raise InvalidAuthDataError
