import logging
from typing import Type

from danielutils import file_exists

from ...constraint_enforcer import ConstraintEnforcer

logger = logging.getLogger(__name__)


class ReadmeEnforcer(ConstraintEnforcer):

    def __init__(self, path: str = "./README.md") -> None:
        self.path = path

    def enforce(self, **kwargs) -> None:
        logger.info(f"Checking for readme file at '{self.path}'")
        
        if not file_exists(self.path):
            logger.error(f"Readme file not found at '{self.path}'")
            raise self.EXCEPTION_TYPE(f"Could not find readme file at '{self.path}'")
        
        logger.info(f"Readme file found at '{self.path}'")


__all__ = [
    "ReadmeEnforcer",
]
