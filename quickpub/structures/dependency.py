from typing import Literal, Callable, Dict

from .version import Version


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

    @staticmethod
    def from_string(s: str) -> 'Dependency':
        # the order of iteration matters, weak inequality operators should be first.
        for op in [">=", "<=", ">", "<", "=="]:
            splits = s.split(op)
            if len(splits) == 2:
                return Dependency(splits[0], op, Version.from_str(splits[-1]))  # type:ignore
        return Dependency(s, ">=", Version(0, 0, 0))

    def __str__(self) -> str:
        if self.ver == Version(0, 0, 0):
            return self.name
        return f"{self.name}{self.operator}{self.ver}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', operator='{self.operator}', version='{self.ver}')"

    def is_satisfied_by(self, ver: Version) -> bool:
        return self._build_func_map()[self.operator](ver)


__all__ = [
    "Dependency"
]
