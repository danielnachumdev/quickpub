from typing import TypeVar

try:
    from typing import TypeAlias
except:
    from typing_extensions import TypeAlias

Path: TypeAlias = TypeVar("Path", bound=str)

__all__ = [
    "Path"
]
