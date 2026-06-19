import logging
from pathlib import Path
from typing import Dict, Union

from danielutils.async_.async_layered_command import AsyncLayeredCommand

from ...package_manager import PackageManager
from ....enforcers import exit_if
from ....structures import Dependency

logger = logging.getLogger(__name__)


class UvPackageManager(PackageManager):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    async def prepare(self, executor: AsyncLayeredCommand) -> None:
        lockfile = self.project_root / "uv.lock"
        exit_if(
            not lockfile.exists(),
            f"uv.lock not found at '{lockfile}'. Run 'uv lock' before using UvPackageManager.",
        )
        logger.debug("Running 'uv sync' for project at '%s'", self.project_root)
        code, _, _ = await executor("uv sync")
        exit_if(code != 0, "Failed executing 'uv sync'")

    async def list_installed(
        self, executor: AsyncLayeredCommand, env_name: str
    ) -> Dict[str, Union[str, Dependency]]:
        return await self._list_installed_from_command(
            executor, env_name, "uv pip list"
        )

    def install_command(self, package: str) -> str:
        return f"uv add --dev {package}"

    def show_command(self, package: str) -> str:
        return f"uv pip show {package}"

    def wrap_command(self, command: str) -> str:
        return f"uv run -- {command}"


__all__ = ["UvPackageManager"]
