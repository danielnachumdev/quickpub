import logging
from danielutils import file_exists

from ...constraint_enforcer import ConstraintEnforcer

logger = logging.getLogger(__name__)


class LicenseEnforcer(ConstraintEnforcer):
    def __init__(self, path: str = "./LICENSE") -> None:
        self.path = path

    def enforce(self, **kwargs) -> None:
        logger.info(f"Checking for license file at '{self.path}'")
        
        if not file_exists(self.path):
            logger.error(f"License file not found at '{self.path}'")
            raise self.EXCEPTION_TYPE(f"Could not find license file at '{self.path}'")
        
        logger.info(f"License file found at '{self.path}'")


__all__ = [
    "LicenseEnforcer",
]
