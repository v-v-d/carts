from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Mapping


class HttpTransportError(Exception):
    def __init__(self, message: str, code: Optional[int] = None) -> None:
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"{self.code} - {self.message}" if self.code else self.message


class IHttpTransport(ABC):
    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[dict[str, Any]] = None,
        params: Optional[Mapping[str, str]] = None,
        data: Optional[dict[Any, Any]] = None,
    ) -> dict[str, Any] | str:
        ...
