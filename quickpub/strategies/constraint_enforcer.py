from abc import abstractmethod

from .quickpub_strategy import QuickpubStrategy


class ConstraintEnforcer(QuickpubStrategy):
    @abstractmethod
    def enforce(self, **kwargs) -> None: ...


__all__ = [
    'ConstraintEnforcer'
]
