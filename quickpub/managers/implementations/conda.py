from typing import Tuple, Optional, Set, Iterator
from danielutils import LayeredCommand, warning

from ..python_manager import PythonManager


class CondaPythonManager(PythonManager):
    def get_python_executable_name(self) -> str:
        return "python"

    def __init__(self, env_names: list[str]) -> None:
        PythonManager.__init__(self, requested_envs=env_names, explicit_versions=[])
        self._cached_available_envs: Optional[Set[str]] = None

    def get_available_envs(self) -> Set[str]:
        if self._cached_available_envs is not None:
            return self._cached_available_envs

        with LayeredCommand(instance_flush_stdout=False, instance_flush_stderr=False) as base:
            code, out, err = base("conda env list")
        res = set([line.split(' ')[0] for line in out[2:] if len(line.split(' ')) > 1])

        self._cached_available_envs = res
        return res

    def __iter__(self) -> Iterator[Tuple[str, LayeredCommand]]:
        available_envs = self.get_available_envs()
        for name in self.requested_envs:
            if name not in available_envs:
                warning(f"Couldn't find env '{name}'")
                continue
            yield name, LayeredCommand(f"conda activate {name}")


__all__ = [
    'CondaPythonManager',
]
