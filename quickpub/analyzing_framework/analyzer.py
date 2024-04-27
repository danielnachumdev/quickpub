from abc import ABC, abstractmethod
from typing import Optional, TypeGuard
from danielutils import get_os, OSType


class Analyzer(ABC):
    PYTHON: str = "python" if get_os() == OSType.WINDOWS else "python3"

    @abstractmethod
    def analyze(self, target_path: str) -> float: ...

    @property
    def use_config_file(self) -> TypeGuard[str]:
        return self.config_file_path is not None

    @property
    def use_executable(self) -> TypeGuard[str]:
        return self.executable_path is not None

    def __init__(self, executable_path: Optional[str] = None, config_file_path: Optional[str] = None) -> None:
        self.executable_path = executable_path
        self.config_file_path = config_file_path


__all__ = [
    "Analyzer"
]
