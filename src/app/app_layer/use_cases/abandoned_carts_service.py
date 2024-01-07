from logging import getLogger
from uuid import UUID

from app.app_layer.interfaces.clients.notifications.client import INotificationsClient
from app.app_layer.interfaces.clients.notifications.dto import SendNotificationInputDTO
from app.app_layer.interfaces.tasks.exceptions import TaskProducingError
from app.app_layer.interfaces.tasks.producer import ITaskProducer
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.config import TaskConfig
from app.domain.cart_notifications.entities import CartNotification
from app.logging import update_context

logger = getLogger(__name__)


class AbandonedCartsService:
    """
    Responsible for processing abandoned carts and sending notifications to the users.
    It uses a unit of work pattern to manage the database transactions and interacts
    with other components such as the task producer and notification client.
    """

    def __init__(
        self,
        uow: IUnitOfWork,
        task_producer: ITaskProducer,
        notification_client: INotificationsClient,
        config: TaskConfig,
    ) -> None:
        self._uow = uow
        self._task_producer = task_producer
        self._notification_client = notification_client
        self._config = config

    @property
    def config(self) -> TaskConfig:
        return self._config

    async def process_abandoned_carts(self) -> None:
        """
        Processes abandoned carts by retrieving the list of abandoned cart IDs and
        enqueuing abandoned cart notification tasks.
        """

        async with self._uow(autocommit=True):
            carts_data = await self._uow.carts.find_abandoned_cart_id_by_user_id()

        logger.debug(
            "Got %s abandoned carts. Ready to send notifications tasks.",
            len(carts_data),
        )

        for user_id, cart_id in carts_data:
            await update_context(cart_id=cart_id)

            try:
                await self._task_producer.enqueue_abandoned_cart_notification_task(
                    cart_id=cart_id,
                    user_id=user_id,
                )
            except TaskProducingError:
                # will be processed next time
                continue

    async def send_notification(self, user_id: int, cart_id: UUID) -> None:
        """Sends a notification to the user for the specified abandoned cart."""

        await update_context(cart_id=cart_id)

        async with self._uow(autocommit=True):
            config = await self._uow.carts.get_config()

        notification = CartNotification.create_abandoned_cart_notification(
            cart_id=cart_id,
            text=config.abandoned_cart_text,
        )

        await self._notification_client.send_notification(
            data=SendNotificationInputDTO(
                user_id=user_id,
                text=notification.text,
            )
        )

        async with self._uow(autocommit=True):
            await self._uow.carts_notifications.create(cart_notification=notification)

        logger.info("Cart %s. Abandoned cart notification successfully sent!", cart_id)
