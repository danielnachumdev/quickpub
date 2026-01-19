import logging
from abc import abstractmethod
from typing import Tuple, Set, List, AsyncIterator

from .quickpub_strategy import QuickpubStrategy
from danielutils.async_.async_layered_command import AsyncLayeredCommand

logger = logging.getLogger(__name__)


class PythonProvider(AsyncIterator, QuickpubStrategy):
    """Base class for Python environment providers. Subclass this to define custom Python environment management strategies."""

    def __init__(
        self,
        auto_install_dependencies: bool = True,
        *,
        requested_envs: List[str],
        explicit_versions: List[str],
        exit_on_fail: bool = False,
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

    async def _get_available_envs(self) -> Set[str]:
        KEY = "__available_envs__"
        if (res := getattr(self, KEY, None)) is not None:
            logger.debug(
                "Using cached available environments for %s", self.__class__.__name__
            )
            return res

        logger.debug("Fetching available environments for %s", self.__class__.__name__)
        setattr(self, KEY, res := await self._get_available_envs_impl())
        logger.debug(
            "Found %d available environments for %s", len(res), self.__class__.__name__
        )
        return res

    @abstractmethod
    async def _get_available_envs_impl(self) -> Set[str]: ...

    def __len__(self) -> int:
        return len(self.requested_envs)

    @abstractmethod
    def get_python_executable_name(self) -> str: ...


__all__ = ["PythonProvider"]
