from typing import Any, Protocol, Optional
from danielutils import get_os, OSType, file_exists


class HasOptionalExecutable():
    PYTHON: str = "python" if get_os() == OSType.WINDOWS else "python3"

    @property
    def use_executable(self) -> bool:
        return self.executable_path is not None

    def __init__(self, name, executable_path: Optional[str] = None) -> None:
        self.name = name
        self.executable_path = executable_path
        if self.use_executable:
            if not file_exists(self.executable_path):
                raise FileNotFoundError(f"Executable not found {self.executable_path}")

    def get_executable(self) -> str:
        if self.use_executable:
            return self.executable_path
        return f"{self.PYTHON} -m {self.name}"


__all__ = [
    'HasOptionalExecutable',
]
