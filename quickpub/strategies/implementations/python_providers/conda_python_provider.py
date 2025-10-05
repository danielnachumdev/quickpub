import logging
from typing import Tuple, Optional, Set, List
from danielutils import AsyncLayeredCommand

from ....enforcers import ExitEarlyError
from ...python_provider import PythonProvider

logger = logging.getLogger(__name__)


class CondaPythonProvider(PythonProvider):
    """Python provider implementation using conda environments."""

    def get_python_executable_name(self) -> str:
        return "python"

    def __init__(self, env_names: List[str]) -> None:
        PythonProvider.__init__(
            self, requested_envs=env_names, explicit_versions=[], exit_on_fail=True)
        self._cached_available_envs: Optional[Set[str]] = None
        logger.info(
            "Initialized CondaPythonProvider with environments: %s", env_names)

    @classmethod
    async def _get_available_envs_impl(cls) -> Set[str]:
        logger.info("Fetching available conda environments")
        with AsyncLayeredCommand() as base:
            code, out, err = await base("conda env list")
        return set([line.split(' ')[0] for line in out[2:] if len(line.split(' ')) > 1])

    async def __anext__(self) -> Tuple[str, AsyncLayeredCommand]:
        if self.aiter_index >= len(self.requested_envs):
            raise StopAsyncIteration

        available_envs = await self.get_available_envs()
        self.aiter_index += 1
        name = self.requested_envs[self.aiter_index - 1]

        logger.debug("Activating conda environment: %s", name)

        if name not in available_envs:
            logger.error(
                "Environment '%s' not found in available conda environments", name)
            raise ExitEarlyError(
                f"Can't find env '{name}' in list of conda environments, try 'conda env list'")

        logger.debug("Successfully activated conda environment: %s", name)
        return name, AsyncLayeredCommand(f"conda activate {name}")


__all__ = [
    'CondaPythonProvider',
]
