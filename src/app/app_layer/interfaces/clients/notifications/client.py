from abc import ABC, abstractmethod

from app.app_layer.interfaces.clients.notifications.dto import SendNotificationInputDTO


class INotificationsClient(ABC):
    @abstractmethod
    async def send_notification(self, data: SendNotificationInputDTO) -> None:
        ...
