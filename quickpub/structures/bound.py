from dataclasses import dataclass
from typing import Literal


@dataclass
class Bound:
    operator: Literal["<", "<=", "==", ">", ">="]
    value: float

    def compare_against(self, score: float) -> bool:
        return {
            ">": score > self.value,
            ">=": score >= self.value,
            "<": score < self.value,
            "<=": score <= self.value,
            "==": score == self.value,
        }[self.operator]

    @staticmethod
    def from_string(s: str) -> 'Bound':
        # the order of iteration matters, weak inequality operators should be first.
        for op in [">=", "<=", "==", ">", "<"]:
            splits = s.split(op)
            if len(splits) == 2:
                return Bound(op, float(splits[-1]))  # type:ignore
        raise ValueError("Invalid 'Bound' format")

    def __str__(self) -> str:
        return f"{self.operator}{self.value}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operator='{self.operator}', value='{self.value}')"


__all__ = [
    'Bound'
]
