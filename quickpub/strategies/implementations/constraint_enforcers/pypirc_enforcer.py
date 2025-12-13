import logging
import re
from typing import Any

from danielutils import file_exists

from ...constraint_enforcer import ConstraintEnforcer

logger = logging.getLogger(__name__)


class PypircEnforcer(ConstraintEnforcer):
    """Enforces the presence and validity of a .pypirc configuration file for PyPI uploads."""

    PYPIRC_REGEX: re.Pattern = re.compile(
        r"\[distutils\]\nindex-servers =\n\s*pypi\n\s*testpypi\n\n\[pypi\]\n\s*username = __token__\n\s*password = .+\n\n\[testpypi\]\n\s*username = __token__\n\s*password = .+\n?"
    )  # pylint: disable=line-too-long

    def __init__(
        self, path: str = "./.pypirc", should_enforce_expected_format: bool = True
    ) -> None:
        self.path = path
        self.should_enforce_expected_format = should_enforce_expected_format

    def enforce(self, **kwargs: Any) -> None:
        logger.info("Validating .pypirc file at '%s'", self.path)

        if not file_exists(self.path):
            logger.error("Could not find .pypirc file at '%s'", self.path)
            raise self.EXCEPTION_TYPE(f"Couldn't find '{self.path}'")

        if self.should_enforce_expected_format:
            with open(self.path, "r") as f:
                text = f.read()

            if not self.PYPIRC_REGEX.match(text):
                logger.error("Invalid .pypirc format at '%s'", self.path)
                raise self.EXCEPTION_TYPE(f"'{self.path}' has an invalid format.")

        logger.info(".pypirc file validation passed for '%s'", self.path)


__all__ = [
    "PypircEnforcer",
]
