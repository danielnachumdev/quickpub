from typing import Literal, Optional

from .version import Version
from .bound import Bound


class Dependency:
    def __init__(self, name: str, operator: Literal["<", "<=", "==", ">", ">="], ver: Optional[Version] = None) -> None:
        self.name = name
        self.operator = operator
        self.ver = ver
        if operator and not ver or not operator and ver:
            raise RuntimeError("Cannot create a 'Dependency' object with only one of parameters 'operator' and 'ver'")
        if not operator and not ver:
            self.operator = ">="
            self.ver = Version(0, 0, 0)

    @staticmethod
    def from_string(s: str) -> 'Dependency':
        # the order of iteration matters, weak inequality operators should be first.
        for op in [">=", "<=", ">", "<", "=="]:
            splits = s.split(op)
            if len(splits) == 2:
                return Dependency(splits[0], op, Version.from_str(splits[-1]))  # type:ignore
        raise ValueError("Invalid 'Dependency' format")

    def __str__(self) -> str:
        if self.ver == Version(0, 0, 0):
            return self.name
        return f"{self.name}{self.operator}{self.ver}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', operator='{self.operator}', version='{self.ver}')"

    def is_satisfied_by(self, ver: Version) -> bool:
        return {
            "==": lambda v: v == self.ver,
            ">=": lambda v: v >= self.ver,
            "<=": lambda v: v <= self.ver,
            ">": lambda v: v > self.ver,
            "<": lambda v: v < self.ver,
        }[self.operator](ver)


__all__ = [
    "Dependency"
]
