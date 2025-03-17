import sys
from typing import Set, Tuple, Iterator, AsyncIterator, Iterable

from danielutils import LayeredCommand
from danielutils.async_.async_layered_command import AsyncLayeredCommand

from ...python_provider import PythonProvider


async def cast_aiter(itr: Iterable) -> AsyncIterator:
    for x in itr:
        yield x


class DefaultPythonProvider(PythonProvider):
    def get_python_executable_name(self) -> str:
        return sys.executable

    def __init__(self) -> None:
        PythonProvider.__init__(self, requested_envs=["system"], explicit_versions=[], exit_on_fail=True)

    async def __anext__(self):
        if self.aiter_index == 0:
            self.aiter_index += 1
            return "system", AsyncLayeredCommand()
        raise StopAsyncIteration

    @classmethod
    def _get_available_envs_impl(cls) -> Set[str]:
        return set("system")


__all__ = [
    "DefaultPythonProvider",
]
