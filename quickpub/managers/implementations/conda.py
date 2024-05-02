from typing import Iterator, Tuple
from danielutils import LayeredCommand, warning

from ..python_manager import PythonManager


class CondaPythonManager(PythonManager):
    def __init__(self, env_names: list[str]) -> None:
        PythonManager.__init__(self, known_envs=env_names, explicit_versions=[])

    def __iter__(self) -> Iterator[Tuple[str, LayeredCommand]]:
        with LayeredCommand("deactivate") as base:
            code, out, err = base("conda env list")
        present_envs = [line.split(' ')[0] for line in out if len(line.split(' ')) > 1]
        for name in self.known_envs:
            if name not in present_envs:
                warning(f"Skipped env {name} because it does not exist")
                continue
            yield name, LayeredCommand(f"conda activate {name}")


__all__ = [
    'CondaPythonManager',
]
