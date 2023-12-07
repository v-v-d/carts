from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class IRetrySystem(ABC):
    @property
    @abstractmethod
    def enabled(self) -> bool:
        ...

    @abstractmethod
    def decorator(self) -> Callable[..., Any]:
        ...
