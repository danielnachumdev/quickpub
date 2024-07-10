from abc import ABC, abstractmethod
from typing import Iterator, Tuple, Set
from danielutils import LayeredCommand


class PythonManager(ABC):
    def __init__(self, auto_install_dependencies: bool = True, *, known_envs: list[str], explicit_versions: list[str],
                 exit_on_fail: bool = False) -> None:
        self.auto_install_dependencies = auto_install_dependencies
        self.requested_envs = known_envs
        self.explicit_versions = explicit_versions
        self.exit_on_fail = exit_on_fail

    @abstractmethod
    def __iter__(self) -> Iterator[Tuple[str, LayeredCommand]]: ...

    @abstractmethod
    def get_available_envs(self) -> Set[str]: ...

    def __len__(self) -> int:
        return len(self.requested_envs)


__all__ = [
    'PythonManager'
]
