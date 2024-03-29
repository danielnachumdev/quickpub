from dataclasses import dataclass


@dataclass(order=True)
class Version:
    @staticmethod
    def from_str(version_str: str) -> "Version":
        return Version(*list(map(int, version_str.split("."))))

    major: int = 0
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass
class Config:
    pylint: bool = False
    mypy: bool = False


__all__ = [
    "Version",
    "Config",
]
