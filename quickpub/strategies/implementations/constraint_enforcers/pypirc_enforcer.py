import logging
import re

from danielutils import file_exists

from ...constraint_enforcer import ConstraintEnforcer

logger = logging.getLogger(__name__)


class PypircEnforcer(ConstraintEnforcer):
    PYPIRC_REGEX: re.Pattern = re.compile(
        r"\[distutils\]\nindex-servers =\n\s*pypi\n\s*testpypi\n\n\[pypi\]\n\s*username = __token__\n\s*password = .+\n\n\[testpypi\]\n\s*username = __token__\n\s*password = .+\n?")  # pylint: disable=line-too-long

    def __init__(self, path: str = "./.pypirc", should_enforce_expected_format: bool = True) -> None:
        self.path = path
        self.should_enforce_expected_format = should_enforce_expected_format

    def enforce(self, **kwargs) -> None:
        logger.info(f"Validating .pypirc file at '{self.path}'")
        
        if not file_exists(self.path):
            logger.error(f"Could not find .pypirc file at '{self.path}'")
            raise self.EXCEPTION_TYPE(f"Couldn't find '{self.path}'")
        
        if self.should_enforce_expected_format:
            with open(self.path, "r") as f:
                text = f.read()

            if not self.PYPIRC_REGEX.match(text):
                logger.error(f"Invalid .pypirc format at '{self.path}'")
                raise self.EXCEPTION_TYPE(f"'{self.path}' has an invalid format.")
        
        logger.info(f".pypirc file validation passed for '{self.path}'")


__all__ = [
    "PypircEnforcer",
]
