from abc import abstractmethod

from danielutils.university.oop.strategy import Strategy


class QuickpubStrategy(Strategy):
    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose

    @abstractmethod
    def execute_strategy(self, *args, **kwargs) -> None: ...


__all__ = [
    'QuickpubStrategy',
]
