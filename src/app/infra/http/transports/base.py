from __future__ import annotations

from abc import ABC, abstractmethod
from http import HTTPMethod
from typing import Any, Mapping

from pydantic import BaseModel

from app.infra.http.retry_systems.base import IRetrySystem


class HttpTransportConfig(BaseModel):
    timeout: int = 5
    integration_name: str


class HttpRequestInputDTO(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    method: HTTPMethod
    url: str
    headers: dict[str, Any] | None = None
    params: Mapping[Any, Any] | list[tuple[Any, Any]] | None = None
    body: list[Any] | dict[Any, Any] | str | None = None


class HttpTransportError(Exception):
    def __init__(self, message: str, code: int | None = None) -> None:
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"{self.code} - {self.message}" if self.code else self.message


class IHttpTransport(ABC):
    @abstractmethod
    async def request(self, data: HttpRequestInputDTO) -> dict[str, Any] | str:
        ...


class RetryableHttpTransport(IHttpTransport):
    def __init__(self, transport: IHttpTransport, retry_system: IRetrySystem) -> None:
        self._transport = transport
        self._retry_system = retry_system

    async def request(
        self, data: HttpRequestInputDTO
    ) -> list[Any] | dict[Any, Any] | str:
        if not self._retry_system.enabled:
            return await self._transport.request(data)

        @self._retry_system.decorator()
        async def retryable_request() -> list[Any] | dict[str, Any] | str:
            return await self._transport.request(data)

        return await retryable_request()
