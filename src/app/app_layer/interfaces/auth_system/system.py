from abc import ABC, abstractmethod

from app.app_layer.interfaces.auth_system.dto import UserDataOutputDTO


class IAuthSystem(ABC):
    @abstractmethod
    def validate_auth_data(self, auth_data: str) -> None:
        ...

    @abstractmethod
    def get_user_data(self, auth_data: str) -> UserDataOutputDTO:
        ...

    @abstractmethod
    def check_for_admin(self, auth_data: str) -> None:
        ...
