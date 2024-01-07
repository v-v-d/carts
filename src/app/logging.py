from contextvars import ContextVar
from logging import LogRecord
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from pythonjsonlogger import jsonlogger


class LoggingConfig(BaseModel):
    level: str
    json_enabled: bool


class ContextDTO(BaseModel):
    cart_id: UUID | None = None
    user_id: int | None = None


ctx: ContextVar[ContextDTO] = ContextVar("current_ctx", default=ContextDTO())


class CtxJsonFormatter(jsonlogger.JsonFormatter):
    def __init__(
        self,
        *args: Any,
        transaction_ctx: ContextVar[BaseModel],
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._ctx = transaction_ctx

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        transaction_ctx = self._ctx.get()
        log_record.update(
            {
                **record.__dict__,
                **transaction_ctx.model_dump(exclude_none=True),
            }
        )


async def update_context(**kwargs) -> None:
    current_ctx = ctx.get()
    ctx.set(current_ctx.model_copy(update={**kwargs}))


def get_logging_config(
    transaction_ctx: ContextVar[BaseModel], config: LoggingConfig
) -> dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
            "json": {
                "()": CtxJsonFormatter,
                "transaction_ctx": transaction_ctx,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": config.level,
                "formatter": "json" if config.json_enabled else "standard",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "root": {
                "handlers": ["console"],
                "level": config.level,
            },
        },
    }
