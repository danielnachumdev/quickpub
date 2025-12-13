import logging
import sys
from typing import Set, Tuple, AsyncIterator, Iterable, Any

from danielutils.async_.async_layered_command import AsyncLayeredCommand

from ...python_provider import PythonProvider

logger = logging.getLogger(__name__)


async def cast_aiter(itr: Iterable[Any]) -> AsyncIterator[Any]:
    for x in itr:
        yield x


class DefaultPythonProvider(PythonProvider):
    """Default Python provider using the system Python interpreter. Provides a single 'system' environment."""

    def get_python_executable_name(self) -> str:
        return sys.executable

    def __init__(self) -> None:
        PythonProvider.__init__(
            self, requested_envs=["system"], explicit_versions=[], exit_on_fail=True
        )
        logger.info(
            "Initialized DefaultPythonProvider with system Python: %s", sys.executable
        )

    async def __anext__(self) -> Tuple[str, AsyncLayeredCommand]:
        if self.aiter_index == 0:
            self.aiter_index += 1
            logger.info("Using system Python environment")
            return "system", AsyncLayeredCommand()
        raise StopAsyncIteration

    @classmethod
    async def _get_available_envs_impl(cls) -> Set[str]:
        return {"system"}


__all__ = [
    "DefaultPythonProvider",
]
