from abc import abstractmethod
from typing import Type

from .quickpub_strategy import QuickpubStrategy


class ConstraintEnforcer(QuickpubStrategy):
    EXCEPTION_TYPE: Type[BaseException] = SystemExit

    @abstractmethod
    def enforce(self, **kwargs) -> None: ...


__all__ = [
    'ConstraintEnforcer'
]
