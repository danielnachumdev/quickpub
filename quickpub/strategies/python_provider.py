import asyncio
import logging

from .quickpub_strategy import QuickpubStrategy
from abc import abstractmethod
from typing import Tuple, Set, List, AsyncIterator, Iterator, Iterable
from danielutils.async_.async_layered_command import AsyncLayeredCommand

logger = logging.getLogger(__name__)


class PythonProvider(AsyncIterator, QuickpubStrategy):
    """Base class for Python environment providers."""
    def __init__(
            self,
            auto_install_dependencies: bool = True,
            *,
            requested_envs: List[str],
            explicit_versions: List[str],
            exit_on_fail: bool = False
    ) -> None:
        self.auto_install_dependencies = auto_install_dependencies
        self.requested_envs = requested_envs
        self.explicit_versions = explicit_versions
        self.exit_on_fail = exit_on_fail
        self.aiter_index = 0

    def __aiter__(self) -> AsyncIterator[Tuple[str, AsyncLayeredCommand]]:
        self.aiter_index = 0
        return self

    @abstractmethod
    async def __anext__(self) -> Tuple[str, AsyncLayeredCommand]: ...

    @classmethod
    async def get_available_envs(cls) -> Set[str]:
        """
        Get available Python environments.
        
        :return: Set of available environment names
        """
        KEY = "__available_envs__"
        if (res := getattr(cls, KEY, None)) is not None:
            logger.debug("Using cached available environments for %s", cls.__name__)
            return res

        logger.debug("Fetching available environments for %s", cls.__name__)
        setattr(cls, KEY, res := await cls._get_available_envs_impl())
        logger.debug("Found %d available environments for %s", len(res), cls.__name__)
        return res

    @classmethod
    @abstractmethod
    async def _get_available_envs_impl(cls) -> Set[str]:
        ...

    def __len__(self) -> int:
        return len(self.requested_envs)

    @abstractmethod
    def get_python_executable_name(self) -> str:
        """
        Get the Python executable name.
        
        :return: Name of the Python executable
        """
        ...


__all__ = [
    'PythonProvider'
]
