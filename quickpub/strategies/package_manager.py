import logging
from abc import abstractmethod
from typing import Dict, Union

from danielutils.async_.async_layered_command import AsyncLayeredCommand

from .quickpub_strategy import QuickpubStrategy
from ..enforcers import exit_if
from ..structures import Dependency
from .implementations.package_managers.installed_package_parser import (
    parse_installed_packages_output,
)

logger = logging.getLogger(__name__)


class PackageManager(QuickpubStrategy):
    async def prepare(self, executor: AsyncLayeredCommand) -> None:
        return None

    @abstractmethod
    async def list_installed(
        self, executor: AsyncLayeredCommand, env_name: str
    ) -> Dict[str, Union[str, Dependency]]: ...

    @abstractmethod
    def install_command(self, package: str) -> str: ...

    @abstractmethod
    def show_command(self, package: str) -> str: ...

    @abstractmethod
    def wrap_command(self, command: str) -> str: ...

    async def _list_installed_from_command(
        self,
        executor: AsyncLayeredCommand,
        env_name: str,
        list_command: str,
    ) -> Dict[str, Union[str, Dependency]]:
        logger.debug(
            "Executing '%s' on environment '%s'", list_command, env_name
        )
        code, out, _ = await executor(list_command)
        exit_if(
            code != 0,
            f"Failed executing '{list_command}' at env '{env_name}'",
        )
        currently_installed = parse_installed_packages_output(out)
        logger.debug("Found %d installed packages", len(currently_installed))
        return currently_installed


__all__ = ["PackageManager"]
