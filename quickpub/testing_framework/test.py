from typing import Optional
from .config import TestingConfiguration


def test(*, test_configurations: Optional[list[TestingConfiguration]] = None) -> None:
    if test_configurations is None:
        return
    for config in test_configurations:
        pass


__all__ = [
    "test"
]
