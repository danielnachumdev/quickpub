from abc import ABC, abstractmethod
from typing import Tuple, Set, Iterator, List
from danielutils import LayeredCommand


class PythonManager(ABC):
    def __init__(self, auto_install_dependencies: bool = True, *, requested_envs: List[str],
                 explicit_versions: List[str],
                 exit_on_fail: bool = False) -> None:
        self.auto_install_dependencies = auto_install_dependencies
        self.requested_envs = requested_envs
        self.explicit_versions = explicit_versions
        self.exit_on_fail = exit_on_fail

    @abstractmethod
    def __iter__(self) -> Iterator[Tuple[str, LayeredCommand]]: ...

    @abstractmethod
    def get_available_envs(self) -> Set[str]: ...

    def __len__(self) -> int:
        return len(self.requested_envs)

    @abstractmethod
    def get_python_executable_name(self) -> str: ...


__all__ = [
    'PythonManager'
]
