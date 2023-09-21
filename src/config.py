from pydantic import BaseModel
from pydantic_settings import BaseSettings


# class DBConfig(BaseModel):
#     url: PostgresDsn
#     connect_args: dict[str, Any] = {}
#     schema_name: str
#
#     @validator("connect_args", pre=True)
#     def _json_to_dict(cls, v: str) -> dict[str, Any]:
#         return orjson.loads(v)
#
#
# class ProductsClientConfig(BaseModel):
#     base_url: AnyHttpUrl


class ArqRedisConfig(BaseModel):
    host: str
    port: int
    password: str | None = None
    database: int = 0
    conn_timeout: int = 60


class Config(BaseSettings):
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

    # PRODUCTS_CLIENT: ProductsClientConfig
    ARQ_REDIS: ArqRedisConfig
    # DB: DBConfig
