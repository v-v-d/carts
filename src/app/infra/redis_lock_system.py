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
    """
    Provides a distributed lock system using Redis as the backend. It allows
    acquiring and releasing locks using the Redis Lock class.
    """

    def __init__(self, redis: Redis, config: RedisLockConfig) -> None:
        self._redis = redis
        self._config = config

        self._lock: Lock | None = None

    async def acquire(self) -> None:
        """
        Acquires a lock using the Redis Lock class. If the lock is already acquired
        by another process, it waits for a specified time or returns immediately
        based on the configuration.
        """

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
            logger.info("Failed to acquire %s because it's already locked!", self._name)
            raise AlreadyLockedError

        logger.debug("Redis lock: %s was successfully acquired!", self._name)

    async def release(self) -> None:
        """Releases the acquired lock using the Redis Lock class."""

        try:
            await self._lock.release()
        except LockError:
            logger.info(
                "Failed to release %s because there is no lock or its ttl has expired!",
                self._name,
            )
            return

        logger.debug("Redis lock: %s was successfully released!", self._name)


async def init_redis(config: RedisLockConfig) -> Generator[Redis, None, None]:
    """
    Initializes a Redis connection and returns a generator object that yields the
    Redis instance.
    """

    redis_pool = ConnectionPool(
        host=config.host,
        port=config.port,
        max_connections=config.pool_size,
    )

    async with Redis(connection_pool=redis_pool) as redis:
        yield redis
