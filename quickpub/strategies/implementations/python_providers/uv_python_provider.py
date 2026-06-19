from pathlib import Path
from typing import Set, Tuple

from danielutils.async_.async_layered_command import AsyncLayeredCommand

from ...python_provider import PythonProvider
from ..package_managers.uv_package_manager import UvPackageManager

import logging

logger = logging.getLogger(__name__)


class UvPythonProvider(PythonProvider):
    def __init__(self, project_root: Path) -> None:
        PythonProvider.__init__(
            self, requested_envs=["uv"], explicit_versions=[], exit_on_fail=True
        )
        self.project_root = project_root
        self.package_manager = UvPackageManager(project_root=project_root)
        logger.info("Initialized UvPythonProvider for project at '%s'", project_root)

    def get_python_executable_name(self) -> str:
        return str(self.project_root / ".venv" / "bin" / "python")

    async def __anext__(self) -> Tuple[str, AsyncLayeredCommand]:
        if self.aiter_index == 0:
            self.aiter_index += 1
            logger.info("Using uv-managed Python environment")
            return "uv", AsyncLayeredCommand()
        raise StopAsyncIteration

    async def _get_available_envs_impl(self) -> Set[str]:
        return {"uv"}


__all__ = ["UvPythonProvider"]
