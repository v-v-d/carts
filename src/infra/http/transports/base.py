from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Mapping


class BaseHttpTransportError(Exception):
    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"{self.code} - {self.message}"


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
