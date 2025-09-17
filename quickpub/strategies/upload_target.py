from abc import abstractmethod

from .quickpub_strategy import QuickpubStrategy


class UploadTarget(QuickpubStrategy):
    """Base class for upload target implementations."""
    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose

    @abstractmethod
    def upload(self, **kwargs) -> None:
        """
        Upload the package.
        
        :param kwargs: Keyword arguments
        """
        ...


__all__ = [
    'UploadTarget',
]
