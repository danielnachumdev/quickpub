import logging
from abc import abstractmethod
from typing import Type

from .quickpub_strategy import QuickpubStrategy

logger = logging.getLogger(__name__)


class BuildSchema(QuickpubStrategy):
    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose
        logger.debug(f"BuildSchema initialized with verbose={verbose}")

    @abstractmethod
    def build(self, *args, **kwargs) -> None: ...


__all__ = [
    "BuildSchema"
]
