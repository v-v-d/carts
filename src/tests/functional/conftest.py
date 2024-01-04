from unittest.mock import AsyncMock, MagicMock

import pytest
from _pytest.fixtures import SubRequest
from aiohttp import ClientSession
from arq import ArqRedis
from pytest_mock import MockerFixture
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.app_layer.interfaces.auth_system.system import IAuthSystem
from app.app_layer.interfaces.clients.coupons.client import ICouponsClient
from app.app_layer.interfaces.clients.notifications.client import INotificationsClient
from app.app_layer.interfaces.clients.products.client import IProductsClient
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.config import RedisLockConfig
from app.infra.auth_system import FakeJWTAuthSystem
from app.infra.events.arq.producers import ArqTaskProducer
from app.infra.http.clients.coupons import CouponsHttpClient
from app.infra.http.clients.notifications import NotificationsHttpClient
from app.infra.http.clients.products import ProductsHttpClient
from app.infra.http.transports.aiohttp import AioHttpTransport
from app.infra.http.transports.base import HttpTransportConfig, IHttpTransport
from app.infra.redis_lock_system import RedisLockSystem
from tests.environment.unit_of_work import TestUow
from tests.utils import fake


@pytest.fixture()
def auth_system() -> IAuthSystem:
    return FakeJWTAuthSystem()


@pytest.fixture()
def redis_lock_config() -> RedisLockConfig:
    return RedisLockConfig(
        host="localhost",
        port=6379,
        pool_size=10,
        conn_timeout_sec=1,
        ttl_sec=10,
        wait_mode=False,
        time_to_wait_sec=0.01,
    )


@pytest.fixture()
def redis(request: SubRequest, mocker: MockerFixture) -> AsyncMock:
    mock = mocker.AsyncMock(spec=Redis)
    mock.register_script.return_value = mocker.AsyncMock()
    mock.set = mocker.AsyncMock()

    if not hasattr(request, "param"):
        return mock

    if "returns" in request.param:
        mock.set.return_value = request.param["returns"]

    return mock


@pytest.fixture()
def distributed_lock_system(
    redis: AsyncMock, redis_lock_config: RedisLockConfig
) -> IDistributedLockSystem:
    return RedisLockSystem(redis=redis, config=redis_lock_config)


@pytest.fixture()
def broker(mocker: MockerFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=ArqRedis)


@pytest.fixture()
def task_producer(broker: AsyncMock) -> ArqTaskProducer:
    return ArqTaskProducer(broker=broker)


@pytest.fixture()
async def uow(session_factory: async_sessionmaker[AsyncSession]) -> TestUow:
    return TestUow(session_factory=session_factory)


@pytest.fixture()
def client_base_url() -> str:
    return fake.internet.url()


@pytest.fixture()
def response_err_text() -> str:
    return fake.text.word()


@pytest.fixture()
def http_response(
    request: SubRequest,
    mocker: MockerFixture,
    response_err_text: str,
) -> AsyncMock:
    mock = mocker.MagicMock()

    if not hasattr(request, "param"):
        return mock

    data_parse_mock = mocker.AsyncMock()

    if "returns" in request.param:
        mock.content_type = "application/json"
        data_parse_mock.return_value = request.param["returns"]
        mock.json = data_parse_mock
    elif "raises" in request.param:
        mock.content_type = "text/html"
        data_parse_mock.return_value = response_err_text
        mock.text = data_parse_mock
        mock.raise_for_status.side_effect = request.param["raises"]

    return mock


@pytest.fixture()
def http_session(mocker: MockerFixture, http_response: AsyncMock) -> MagicMock:
    mock = mocker.MagicMock(spec=ClientSession)
    mock.request.return_value.__aenter__.return_value = http_response

    return mock


@pytest.fixture()
def http_config() -> HttpTransportConfig:
    return HttpTransportConfig(integration_name="test")


@pytest.fixture()
def client_transport(
    http_session: AsyncMock, http_config: HttpTransportConfig
) -> IHttpTransport:
    return AioHttpTransport(session=http_session, config=http_config)


@pytest.fixture()
def products_client(
    client_base_url: str, client_transport: IHttpTransport
) -> IProductsClient:
    return ProductsHttpClient(base_url=client_base_url, transport=client_transport)


@pytest.fixture()
def coupons_client(
    client_base_url: str, client_transport: IHttpTransport
) -> ICouponsClient:
    return CouponsHttpClient(base_url=client_base_url, transport=client_transport)


@pytest.fixture()
def notifications_client(
    client_base_url: str, client_transport: IHttpTransport
) -> INotificationsClient:
    return NotificationsHttpClient(base_url=client_base_url, transport=client_transport)
