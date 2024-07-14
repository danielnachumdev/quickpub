from abc import abstractmethod

from .quickpub_strategy import QuickpubStrategy


class UploadTarget(QuickpubStrategy):
    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose

    @abstractmethod
    def execute_strategy(self, *args, **kwargs) -> None: ...


__all__ = [
    'UploadTarget',
]
