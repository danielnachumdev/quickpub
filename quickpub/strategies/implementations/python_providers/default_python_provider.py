import sys
from typing import Set, Tuple, Iterator

from danielutils import LayeredCommand

from ...python_provider import PythonProvider


class DefaultInterpreterProvider(PythonProvider):
    def get_python_executable_name(self) -> str:
        return sys.executable

    def __init__(self) -> None:
        PythonProvider.__init__(self, requested_envs=["system"], explicit_versions=[], exit_on_fail=True)

    def __iter__(self) -> Iterator[Tuple[str, LayeredCommand]]:
        return iter([("system", LayeredCommand(""))])

    def get_available_envs(self) -> Set[str]:
        return set("system")


__all__ = [
    "DefaultInterpreterProvider",
]
