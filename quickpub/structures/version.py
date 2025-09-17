import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(order=True)
class Version:
    """Represents a semantic version with major, minor, and patch components."""
    @staticmethod
    def from_str(version_str: str) -> "Version":
        """
        Create a Version from a string representation.
        
        :param version_str: String representation of the version
        :return: Version object
        :raises ValueError: If string format is invalid
        """
        logger.debug("Parsing version from string: '%s'", version_str)
        try:
            version = Version(*list(map(int, version_str.split("."))))
            logger.debug("Parsed version: %s", version)
            return version
        except Exception as e:
            logger.error("Failed to parse version from string '%s': %s", version_str, e)
            raise ValueError(f"Failed converting '{version_str}' to instance of 'Version' in 'Version.from_str") from e

    major: int = 0
    minor: int = 0
    patch: int = 0

    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0):
        if not all(map(lambda x: isinstance(x, int) and x >= 0, [major, minor, patch])):
            logger.error("Invalid version components: major=%s, minor=%s, patch=%s", major, minor, patch)
            raise ValueError("Version supports positive integers only")
        self.major = major
        self.minor = minor
        self.patch = patch
        logger.debug("Version created: %s", self)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


__all__ = [
    'Version'
]
