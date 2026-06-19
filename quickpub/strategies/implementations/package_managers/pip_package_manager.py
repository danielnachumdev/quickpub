import logging
from typing import Dict, Union

from danielutils.async_.async_layered_command import AsyncLayeredCommand

from ...package_manager import PackageManager
from ....structures import Dependency

logger = logging.getLogger(__name__)


class PipPackageManager(PackageManager):
    async def prepare(self, executor: AsyncLayeredCommand) -> None:
        return None

    async def list_installed(
        self, executor: AsyncLayeredCommand, env_name: str
    ) -> Dict[str, Union[str, Dependency]]:
        return await self._list_installed_from_command(executor, env_name, "pip list")

    def install_command(self, package: str) -> str:
        return f"pip install {package}"

    def show_command(self, package: str) -> str:
        return f"pip show {package}"

    def wrap_command(self, command: str) -> str:
        return command


__all__ = ["PipPackageManager"]
