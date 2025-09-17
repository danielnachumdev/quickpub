import logging
from typing import Type

from danielutils import file_exists

from ...constraint_enforcer import ConstraintEnforcer

logger = logging.getLogger(__name__)


class ReadmeEnforcer(ConstraintEnforcer):
    """Enforces the presence of a README file."""

    def __init__(self, path: str = "./README.md") -> None:
        self.path = path

    def enforce(self, **kwargs) -> None:
        logger.info("Checking for readme file at '%s'", self.path)

        if not file_exists(self.path):
            logger.error("Readme file not found at '%s'", self.path)
            raise self.EXCEPTION_TYPE(f"Could not find readme file at '{self.path}'")

        logger.info("Readme file found at '%s'", self.path)


__all__ = [
    "ReadmeEnforcer",
]
