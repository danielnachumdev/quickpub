from abc import ABC, abstractmethod
from typing import Iterator, Tuple
from danielutils import LayeredCommand


class PythonManager(ABC):
    def __init__(self, *, known_envs: list[str], explicit_versions: list[str], exit_on_fail: bool = False) -> None:
        self.known_envs = known_envs
        self.explicit_versions = explicit_versions
        self.exit_on_fail = exit_on_fail

    @abstractmethod
    def __iter__(self) -> Iterator[Tuple[str, LayeredCommand]]: ...


__all__ = [
    'PythonManager'
]
