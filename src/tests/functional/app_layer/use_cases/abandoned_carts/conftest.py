import pytest

from app.app_layer.interfaces.clients.notifications.client import INotificationsClient
from app.app_layer.interfaces.tasks.producer import ITaskProducer
from app.app_layer.use_cases.abandoned_carts_service import AbandonedCartsService
from app.config import TaskConfig
from tests.environment.unit_of_work import TestUow
from tests.utils import fake


@pytest.fixture()
def task_config() -> TaskConfig:
    return TaskConfig(
        max_tries=fake.numeric.integer_number(start=1),
        retry_delay_sec=fake.numeric.integer_number(start=1),
    )


@pytest.fixture()
def service(
    uow: TestUow,
    task_producer: ITaskProducer,
    notifications_client: INotificationsClient,
    task_config: TaskConfig,
) -> AbandonedCartsService:
    return AbandonedCartsService(
        uow=uow,
        task_producer=task_producer,
        notification_client=notifications_client,
        config=task_config,
    )
