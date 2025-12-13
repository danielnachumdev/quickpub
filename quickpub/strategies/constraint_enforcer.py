from abc import abstractmethod
from typing import Any, Type

from ..enforcers import ExitEarlyError
from .quickpub_strategy import QuickpubStrategy


class ConstraintEnforcer(QuickpubStrategy):
    """Base class for constraint enforcer implementations. Subclass this to define custom constraint validation logic."""

    EXCEPTION_TYPE: Type[Exception] = ExitEarlyError

    @abstractmethod
    def enforce(self, **kwargs: Any) -> None: ...


__all__ = ["ConstraintEnforcer"]
