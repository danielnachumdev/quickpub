import logging
from danielutils import file_exists

from ...constraint_enforcer import ConstraintEnforcer

logger = logging.getLogger(__name__)


class LicenseEnforcer(ConstraintEnforcer):
    """Enforces the presence of a license file at the specified path."""

    def __init__(self, path: str = "./LICENSE") -> None:
        self.path = path

    def enforce(self, **kwargs) -> None:
        logger.info("Checking for license file at '%s'", self.path)

        if not file_exists(self.path):
            logger.error("License file not found at '%s'", self.path)
            raise self.EXCEPTION_TYPE(f"Could not find license file at '{self.path}'")

        logger.info("License file found at '%s'", self.path)


__all__ = [
    "LicenseEnforcer",
]
