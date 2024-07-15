from typing import Type

from danielutils.university.oop.strategy import Strategy


class QuickpubStrategy(Strategy):
    EXCEPTION_TYPE: Type[Exception] = SystemExit


__all__ = [
    'QuickpubStrategy',
]
