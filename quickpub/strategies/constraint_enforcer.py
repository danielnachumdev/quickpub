from abc import abstractmethod
from typing import Type

from ..enforcers import ExitEarlyError
from .quickpub_strategy import QuickpubStrategy


class ConstraintEnforcer(QuickpubStrategy):
    """Base class for constraint enforcer implementations."""
    EXCEPTION_TYPE: Type[Exception] = ExitEarlyError

    @abstractmethod
    def enforce(self, **kwargs) -> None:
        """
        Enforce the constraint.
        
        :param kwargs: Keyword arguments
        """
        ...


__all__ = [
    'ConstraintEnforcer'
]
