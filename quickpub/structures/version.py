from dataclasses import dataclass


@dataclass(order=True)
class Version:
    @staticmethod
    def from_str(version_str: str) -> "Version":
        try:
            return Version(*list(map(int, version_str.split("."))))
        except Exception as e:
            raise ValueError(f"Failed converting '{version_str}' to instance of 'Version' in 'Version.from_str") from e


    major: int = 0
    minor: int = 0
    patch: int = 0

    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0):
        if not all(map(lambda x: isinstance(x, int) and x >= 0, [major, minor, patch])):
            raise ValueError("Version supports positive integers only")
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


__all__ = [
    'Version'
]
