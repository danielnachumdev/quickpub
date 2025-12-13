from typing import Type

from danielutils.university.oop.strategy import Strategy

from ..enforcers import ExitEarlyError


class QuickpubStrategy(Strategy):
    EXCEPTION_TYPE: Type[Exception] = ExitEarlyError


__all__ = [
    "QuickpubStrategy",
]
