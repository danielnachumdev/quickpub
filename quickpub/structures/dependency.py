import logging
from typing import Literal, Callable, Dict, Any

from .version import Version

logger = logging.getLogger(__name__)


class Dependency:
    def _build_func_map(self) -> Dict[str, Callable[[Version], bool]]:
        return {
            "==": lambda v: v == self.ver,
            ">=": lambda v: v >= self.ver,
            "<=": lambda v: v <= self.ver,
            ">": lambda v: v > self.ver,
            "<": lambda v: v < self.ver,
        }

    def __init__(self, name: str, operator: Literal["<", "<=", "==", ">", ">="] = ">=",
                 ver: Version = Version(0, 0, 0)) -> None:
        self.name: str = name
        self.operator: Literal["<", "<=", "==", ">", ">="] = operator
        self.ver: Version = ver or Version(0, 0, 0)
        logger.debug(f"Dependency created: {self.name} {self.operator} {self.ver}")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Dependency):
            return False
        return self.name == other.name and self.operator == other.operator and self.ver == other.ver

    def __hash__(self) -> int:
        return hash((self.name, self.operator, self.ver))

    @staticmethod
    def from_string(s: str) -> 'Dependency':
        logger.debug(f"Parsing dependency from string: '{s}'")
        # the order of iteration matters, weak inequality operators should be first.
        for op in [">=", "<=", ">", "<", "=="]:
            splits = s.split(op)
            if len(splits) == 2:
                dep = Dependency(splits[0], op, Version.from_str(splits[-1]))  # type:ignore
                logger.debug(f"Parsed dependency: {dep}")
                return dep
        dep = Dependency(s, ">=", Version(0, 0, 0))
        logger.debug(f"Parsed dependency (default): {dep}")
        return dep

    def __str__(self) -> str:
        if self.ver == Version(0, 0, 0):
            return self.name
        return f"{self.name}{self.operator}{self.ver}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', operator='{self.operator}', version='{self.ver}')"

    def is_satisfied_by(self, ver: Version) -> bool:
        result = self._build_func_map()[self.operator](ver)
        logger.debug(f"Dependency '{self}' satisfied by version '{ver}': {result}")
        return result


__all__ = [
    "Dependency"
]
