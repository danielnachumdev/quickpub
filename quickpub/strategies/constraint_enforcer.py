from abc import abstractmethod
from typing import Type

from ..enforcers import ExitEarlyError
from .quickpub_strategy import QuickpubStrategy


class ConstraintEnforcer(QuickpubStrategy):
    EXCEPTION_TYPE: Type[Exception] = ExitEarlyError

    @abstractmethod
    def enforce(self, **kwargs) -> None: ...


__all__ = [
    'ConstraintEnforcer'
]
