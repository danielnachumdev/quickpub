import logging
import re

from danielutils import file_exists

from ..constraint_enforcers import PypircEnforcer
from ...upload_target import UploadTarget

logger = logging.getLogger(__name__)


class PypircUploadTarget(UploadTarget):
    """Upload target implementation using .pypirc configuration. Uploads packages to PyPI using twine."""

    REGEX_PATTERN: re.Pattern = PypircEnforcer.PYPIRC_REGEX

    def upload(self, name: str, version: str, **kwargs) -> None:  # type: ignore
        from quickpub.proxy import cm
        from quickpub.enforcers import exit_if

        logger.info("Starting PyPI upload for package '%s' version '%s'", name, version)

        self._validate_file_exists()
        self._validate_file_contents()

        if self.verbose:
            logger.info("Uploading package to PyPI")

        ret, stdout, stderr = cm(
            "twine",
            "upload",
            "--config-file",
            ".pypirc",
            f"dist/{name}-{version}.tar.gz",
        )

        if ret != 0:
            logger.error("PyPI upload failed with return code %d: %s", ret, stderr)
            exit_if(
                ret != 0,
                f"Failed uploading the package to pypi. Try running the following command manually:\n\ttwine upload --config-file .pypirc dist/{name}-{version}.tar.gz",
            )

        logger.info(
            "Successfully uploaded package '%s' version '%s' to PyPI", name, version
        )

    def _validate_file_exists(self) -> None:
        logger.debug("Validating .pypirc file exists at '%s'", self.pypirc_file_path)
        if not file_exists(self.pypirc_file_path):
            logger.error(".pypirc file not found at '%s'", self.pypirc_file_path)
            raise RuntimeError(
                f"{self.__class__.__name__} can't find pypirc file at '{self.pypirc_file_path}'"
            )
        logger.debug(".pypirc file found at '%s'", self.pypirc_file_path)

    def _validate_file_contents(self) -> None:
        logger.debug("Validating .pypirc file contents at '%s'", self.pypirc_file_path)
        with open(self.pypirc_file_path, "r", encoding="utf8") as f:
            text = f.read()
        if not self.REGEX_PATTERN.match(text):
            logger.error(
                ".pypirc file contents validation failed for '%s'",
                self.pypirc_file_path,
            )
            raise RuntimeError(
                f"{self.__class__.__name__} checked the contents of '{self.pypirc_file_path}' and it failed to match the following regex: r\"{self.REGEX_PATTERN.pattern}\""
            )
        logger.debug(
            ".pypirc file contents validation passed for '%s'", self.pypirc_file_path
        )

    def __init__(
        self, pypirc_file_path: str = "./.pypirc", verbose: bool = False
    ) -> None:
        super().__init__(verbose)
        self.pypirc_file_path = pypirc_file_path
        logger.info(
            "Initialized PypircUploadTarget with pypirc_file_path='%s', verbose=%s",
            pypirc_file_path,
            verbose,
        )


__all__ = ["PypircUploadTarget"]
