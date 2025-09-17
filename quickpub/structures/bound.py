import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class Bound:
    operator: Literal["<", "<=", "==", ">", ">="]
    value: float

    def compare_against(self, score: float) -> bool:
        result = {
            ">": score > self.value,
            ">=": score >= self.value,
            "<": score < self.value,
            "<=": score <= self.value,
            "==": score == self.value,
        }[self.operator]
        logger.debug(f"Bound comparison: {score} {self.operator} {self.value} = {result}")
        return result

    @staticmethod
    def from_string(s: str) -> 'Bound':
        logger.debug(f"Parsing bound from string: '{s}'")
        # the order of iteration matters, weak inequality operators should be first.
        for op in [">=", "<=", "==", ">", "<"]:
            splits = s.split(op)
            if len(splits) == 2:
                bound = Bound(op, float(splits[-1]))  # type:ignore
                logger.debug(f"Parsed bound: {bound}")
                return bound
        logger.error(f"Failed to parse bound from string: '{s}'")
        raise ValueError("Invalid 'Bound' format")

    def __str__(self) -> str:
        return f"{self.operator}{self.value}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operator='{self.operator}', value='{self.value}')"


__all__ = [
    'Bound'
]
