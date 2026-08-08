import logging
from typing import Any

from danielutils import file_exists, LayeredCommand

from ...build_schema import BuildSchema

logger = logging.getLogger(__name__)


class UvBuildSchema(BuildSchema):
    def __init__(
        self,
        pyproject_path: str = "./pyproject.toml",
        sdist: bool = True,
        wheel: bool = True,
    ) -> None:
        if not sdist and not wheel:
            raise self.EXCEPTION_TYPE(
                "UvBuildSchema requires at least one of sdist or wheel"
            )
        self._pyproject_path = pyproject_path
        self._sdist = sdist
        self._wheel = wheel

    def build_command(self) -> str:
        if self._sdist and self._wheel:
            return "uv build"
        if self._sdist:
            return "uv build --sdist"
        return "uv build --wheel"

    def build(self, verbose: bool = False, *args: Any, **kwargs: Any) -> None:
        if not file_exists(self._pyproject_path):
            logger.error("pyproject.toml not found: %s", self._pyproject_path)
            raise self.EXCEPTION_TYPE(f"Could not find {self._pyproject_path} file")

        command = self.build_command()
        if verbose:
            logger.info("Creating new distribution with '%s'...", command)

        with LayeredCommand() as executor:
            ret, stdout, stderr = executor(command)

        if ret != 0:
            logger.error("Build command failed with return code %d: %s", ret, stderr)
            raise self.EXCEPTION_TYPE(stderr)


__all__ = ["UvBuildSchema"]
