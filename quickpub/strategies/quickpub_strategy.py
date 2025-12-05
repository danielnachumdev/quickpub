from typing import Type

from danielutils.university.oop.strategy import Strategy

from ..enforcers import ExitEarlyError


class QuickpubStrategy(Strategy):
    """Base strategy class for quickpub operations."""

    EXCEPTION_TYPE: Type[Exception] = ExitEarlyError


__all__ = [
    "QuickpubStrategy",
]
