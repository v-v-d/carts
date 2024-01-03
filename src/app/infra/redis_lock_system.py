from collections.abc import Generator
from logging import getLogger

from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.lock import Lock
from redis.exceptions import LockError

from app.app_layer.interfaces.distributed_lock_system.exceptions import AlreadyLockedError
from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.config import RedisLockConfig

logger = getLogger(__name__)


class RedisLockSystem(IDistributedLockSystem):
    def __init__(self, redis: Redis, config: RedisLockConfig) -> None:
        self._redis = redis
        self._config = config

        self._lock: Lock | None = None

    async def acquire(self) -> None:
        self._lock = Lock(
            redis=self._redis,
            name=self._name,
            timeout=self._config.ttl_sec,
            sleep=self._config.acquire_tries_interval_sec,
            blocking=self._config.wait_mode,
            blocking_timeout=self._config.time_to_wait_sec,
        )

        acquired = await self._lock.acquire()

        if not acquired:
            logger.info(f"Failed to acquire {self._name} because it's already locked!")
            raise AlreadyLockedError

        logger.debug(f"Redis lock: {self._name} was successfully acquired!")

    async def release(self) -> None:
        try:
            await self._lock.release()
        except LockError:
            logger.info(
                f"Failed to release {self._name} because there is no lock or its ttl has expired!"
            )
            return

        logger.debug(f"Redis lock: {self._name} was successfully released!")


async def init_redis(config: RedisLockConfig) -> Generator[Redis, None, None]:
    redis_pool = ConnectionPool(
        host=config.host,
        port=config.port,
        max_connections=config.pool_size,
    )

    async with Redis(connection_pool=redis_pool) as redis:
        yield redis
