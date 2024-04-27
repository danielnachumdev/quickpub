from dataclasses import dataclass
from typing import Optional
from .analyzing_framework import StaticAnalyzersConfig
from .testing_framework import TestingConfiguration


@dataclass(order=True)
class Version:
    @staticmethod
    def from_str(version_str: str) -> "Version":
        return Version(*list(map(int, version_str.split("."))))

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


@dataclass(frozen=True)
class AdditionalConfiguration:
    analyzers: Optional[list[StaticAnalyzersConfig]] = None
    testers: Optional[list[TestingConfiguration]] = None


__all__ = [
    "Version",
    'AdditionalConfiguration'
]
