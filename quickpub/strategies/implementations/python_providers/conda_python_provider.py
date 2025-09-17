import logging
from typing import Tuple, Optional, Set, List
from danielutils import AsyncLayeredCommand

from ....enforcers import ExitEarlyError
from ...python_provider import PythonProvider

logger = logging.getLogger(__name__)


class CondaPythonProvider(PythonProvider):
    def get_python_executable_name(self) -> str:
        return "python"

    def __init__(self, env_names: List[str]) -> None:
        PythonProvider.__init__(self, requested_envs=env_names, explicit_versions=[], exit_on_fail=True)
        self._cached_available_envs: Optional[Set[str]] = None
        logger.info(f"Initialized CondaPythonProvider with environments: {env_names}")

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
        
        logger.info(f"Activating conda environment: {name}")
        
        if name not in available_envs:
            logger.error(f"Environment '{name}' not found in available conda environments")
            raise ExitEarlyError(f"Can't find env '{name}' in list of conda environments, try 'conda env list'")
        
        logger.info(f"Successfully activated conda environment: {name}")
        return name, AsyncLayeredCommand(f"conda activate {name}")


__all__ = [
    'CondaPythonProvider',
]
