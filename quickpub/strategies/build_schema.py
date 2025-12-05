import logging
from abc import abstractmethod

from .quickpub_strategy import QuickpubStrategy

logger = logging.getLogger(__name__)


class BuildSchema(QuickpubStrategy):
    """Base class for build schema implementations."""

    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose
        logger.debug("BuildSchema initialized with verbose=%s", verbose)

    @abstractmethod
    def build(self, *args, **kwargs) -> None:
        """
        Build the package.

        :param args: Positional arguments
        :param kwargs: Keyword arguments
        """
        ...


__all__ = ["BuildSchema"]
