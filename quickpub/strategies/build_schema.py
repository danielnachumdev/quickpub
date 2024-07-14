from abc import abstractmethod

from .quickpub_strategy import QuickpubStrategy


class BuildSchema(QuickpubStrategy):
    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose

    @abstractmethod
    def build(self, *args, **kwargs) -> None: ...


__all__ = [
    "BuildSchema"
]
