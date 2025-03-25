import asyncio

from .quickpub_strategy import QuickpubStrategy
from abc import abstractmethod
from typing import Tuple, Set, List, AsyncIterator, Iterator, Iterable
from danielutils.async_.async_layered_command import AsyncLayeredCommand


class PythonProvider(AsyncIterator, QuickpubStrategy):
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
        KEY = "__available_envs__"
        if (res := getattr(cls, KEY, None)) is not None:
            return res

        setattr(cls, KEY, res := await cls._get_available_envs_impl())
        return res

    @classmethod
    @abstractmethod
    async def _get_available_envs_impl(cls) -> Set[str]:
        ...

    def __len__(self) -> int:
        return len(self.requested_envs)

    @abstractmethod
    def get_python_executable_name(self) -> str:
        ...


__all__ = [
    'PythonProvider'
]
