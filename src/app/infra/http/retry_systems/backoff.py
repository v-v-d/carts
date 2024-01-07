from collections.abc import Callable
from http import HTTPStatus
from logging import getLogger
from typing import Any

from backoff import constant, expo, on_exception
from backoff._typing import Details
from pydantic import BaseModel

from app.infra.http.retry_systems.base import IRetrySystem
from app.infra.http.transports.base import HttpTransportError

logger = getLogger(__name__)


class BackoffConfig(BaseModel):
    enabled: bool
    max_retries: int = 3
    retry_status_codes: set[int] = {
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    }
    constant_wait_gen_interval: float | None = None


class BackoffRetrySystem(IRetrySystem):
    """
    Provides a decorator method that can be used to retry a function call with
    backoff and giveup strategies based on the provided configuration.
    """

    def __init__(self, config: BackoffConfig) -> None:
        self._config = config

    @property
    def enabled(self) -> bool:
        return self._config.enabled

    def decorator(self) -> Callable[..., Any]:
        """
        Returns a decorator function that can be used to retry a function call.
        """

        common_kwargs = {
            "max_tries": self._config.max_retries,
            "giveup": self._on_giveup,
            "on_backoff": self._on_backoff,
            "exception": HttpTransportError,
        }

        if self._config.constant_wait_gen_interval:
            return on_exception(
                wait_gen=constant,
                interval=self._config.constant_wait_gen_interval,
                **common_kwargs,  # type: ignore [arg-type]
            )

        return on_exception(wait_gen=expo, **common_kwargs)  # type: ignore [arg-type]

    @staticmethod
    def _on_backoff(details: Details) -> None:
        logger.info(
            "Backing off {wait:0.1f} seconds afters {tries} tries request method "
            "with args {args} and kwargs {kwargs}".format(**details),
        )

    def _on_giveup(self, error: HttpTransportError) -> bool:
        return not error.code or error.code not in self._config.retry_status_codes
