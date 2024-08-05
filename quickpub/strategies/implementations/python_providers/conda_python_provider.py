from typing import Tuple, Optional, Set, Iterator, List
from danielutils import LayeredCommand, warning

from ...python_provider import PythonProvider


class CondaPythonProvider(PythonProvider):
    def get_python_executable_name(self) -> str:
        return "python"

    def __init__(self, env_names: List[str]) -> None:
        PythonProvider.__init__(self, requested_envs=env_names, explicit_versions=[], exit_on_fail=True)
        self._cached_available_envs: Optional[Set[str]] = None

    @classmethod
    def _get_available_envs_impl(cls) -> Set[str]:
        with LayeredCommand() as base:
            code, out, err = base("conda env list")
        return set([line.split(' ')[0] for line in out[2:] if len(line.split(' ')) > 1])

    def __iter__(self) -> Iterator[Tuple[str, LayeredCommand]]:
        available_envs = self.get_available_envs()
        for name in self.requested_envs:
            if name not in available_envs:
                warning(f"Couldn't find env '{name}'")
                continue
            yield name, LayeredCommand(f"conda activate {name}")


__all__ = [
    'CondaPythonProvider',
]
