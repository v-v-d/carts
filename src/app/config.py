from typing import Any

from pydantic import AnyHttpUrl, BaseModel, PostgresDsn
from pydantic_settings import BaseSettings

from app.logging import LoggingConfig


class DBConfig(BaseModel):
    app_name: str
    dsn: PostgresDsn
    schema_name: str
    pool_size: int
    timezone: str
    max_overflow: int
    pool_pre_ping: bool
    connection_timeout: int
    command_timeout: int
    server_settings: dict[str, Any] = {}
    connect_args: dict[str, Any] = {}
    debug: bool = False
    graph_name: str = "template"


class ProductsClientConfig(BaseModel):
    name: str
    base_url: AnyHttpUrl
    retries_enabled: bool


class CouponsClientConfig(BaseModel):
    name: str
    base_url: AnyHttpUrl
    retries_enabled: bool


class NotificationsClientConfig(BaseModel):
    name: str
    base_url: AnyHttpUrl
    retries_enabled: bool


class ArqRedisConfig(BaseModel):
    host: str
    port: int
    password: str | None = None
    database: int = 0
    conn_timeout: int = 60


class TaskConfig(BaseModel):
    max_tries: int
    retry_delay_sec: int
    no_keep_result_value: int = 0


class PeriodicConfig(BaseModel):
    schedule: dict[str, Any] = {"hour": [0, 12]}


class RedisLockConfig(BaseModel):
    host: str
    port: int
    pool_size: int
    conn_timeout_sec: int = 60
    ttl_sec: float
    acquire_tries_interval_sec: float = 0.1
    wait_mode: bool = True
    time_to_wait_sec: float = 5.0


class Config(BaseSettings):
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

    PRODUCTS_CLIENT: ProductsClientConfig
    COUPONS_CLIENT: CouponsClientConfig
    NOTIFICATIONS_CLIENT: NotificationsClientConfig
    ARQ_REDIS: ArqRedisConfig
    TASK: TaskConfig
    PERIODIC: PeriodicConfig
    DB: DBConfig
    LOGGING: LoggingConfig
    REDIS_LOCK: RedisLockConfig
