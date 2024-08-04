from .quickpub_strategy import QuickpubStrategy
from .quality_assurance_runner import QualityAssuranceRunner
from abc import abstractmethod
from typing import Tuple, Set, Iterator, List
from danielutils import LayeredCommand


class PythonProvider(QuickpubStrategy):
    def __init__(self, auto_install_dependencies: bool = True, *, requested_envs: List[str],
                 explicit_versions: List[str],
                 exit_on_fail: bool = False) -> None:
        self.auto_install_dependencies = auto_install_dependencies
        self.requested_envs = requested_envs
        self.explicit_versions = explicit_versions
        self.exit_on_fail = exit_on_fail

    @abstractmethod
    def __iter__(self) -> Iterator[Tuple[str, LayeredCommand]]: ...

    @classmethod
    def get_available_envs(cls) -> Set[str]:
        KEY = "__available_envs__"
        if (res := getattr(cls, KEY, None)) is not None:
            return res

        setattr(cls, KEY, res := cls._get_available_envs_impl())
        return res

    @classmethod
    @abstractmethod
    def _get_available_envs_impl(cls) -> Set[str]: ...

    def __len__(self) -> int:
        return len(self.requested_envs)

    @abstractmethod
    def get_python_executable_name(self) -> str: ...


__all__ = [
    'PythonProvider'
]
