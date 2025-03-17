from typing import Tuple, Optional, Set, Iterator, List, AsyncIterator
from danielutils import LayeredCommand, warning
from danielutils.async_.async_layered_command import AsyncLayeredCommand

from ...python_provider import PythonProvider


class CondaPythonProvider(PythonProvider):
    def get_python_executable_name(self) -> str:
        return "python"

    def __init__(self, env_names: List[str]) -> None:
        PythonProvider.__init__(self, requested_envs=env_names, explicit_versions=[], exit_on_fail=True)
        self._cached_available_envs: Optional[Set[str]] = None

    @classmethod
    async def _get_available_envs_impl(cls) -> Set[str]:
        with AsyncLayeredCommand() as base:
            code, out, err = await base("conda env list")
        return set([line.split(' ')[0] for line in out[2:] if len(line.split(' ')) > 1])

    async def __anext__(self) -> Tuple[str, AsyncLayeredCommand]:
        if self.aiter_index >= len(self.requested_envs):
            raise StopAsyncIteration
        available_envs = await self.get_available_envs()
        self.aiter_index += 1
        name = self.requested_envs[self.aiter_index - 1]
        if name not in available_envs:
            warning(f"Couldn't find env '{name}'")
            return name, None
        return name, AsyncLayeredCommand(f"conda activate {name}")


__all__ = [
    'CondaPythonProvider',
]
