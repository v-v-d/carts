from decimal import Decimal
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


class ProductsClientConfig(BaseModel):
    name: str
    base_url: AnyHttpUrl
    retries_enabled: bool


class ArqRedisConfig(BaseModel):
    host: str
    port: int
    password: str | None = None
    database: int = 0
    conn_timeout: int = 60


class CartRestrictionsConfig(BaseModel):
    max_items_qty: int = 30
    min_cost_for_checkout: int = 500


class CartConfig(BaseModel):
    restrictions: CartRestrictionsConfig
    weight_item_qty: Decimal = Decimal(1)


class Config(BaseSettings):
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

    PRODUCTS_CLIENT: ProductsClientConfig
    ARQ_REDIS: ArqRedisConfig
    DB: DBConfig
    LOGGING: LoggingConfig
    CART: CartConfig
