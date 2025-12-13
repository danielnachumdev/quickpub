from abc import abstractmethod

from .quickpub_strategy import QuickpubStrategy


class UploadTarget(QuickpubStrategy):
    """Base class for upload target implementations. Subclass this to define custom upload strategies."""

    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose

    @abstractmethod
    def upload(self, **kwargs) -> None: ...


__all__ = [
    "UploadTarget",
]
