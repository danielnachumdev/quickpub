import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class Bound:
    """Represents a bound constraint for quality assurance scoring."""

    operator: Literal["<", "<=", "==", ">", ">="]
    value: float

    def compare_against(self, score: float) -> bool:
        """
        Compare a score against this bound.

        :param score: Score to compare
        :return: True if score satisfies the bound
        """
        result = {
            ">": score > self.value,
            ">=": score >= self.value,
            "<": score < self.value,
            "<=": score <= self.value,
            "==": score == self.value,
        }[self.operator]
        logger.debug(
            "Bound comparison: %s %s %s = %s", score, self.operator, self.value, result
        )
        return result

    @staticmethod
    def from_string(s: str) -> "Bound":
        """
        Create a Bound from a string representation.

        :param s: String representation of the bound
        :return: Bound object
        :raises ValueError: If string format is invalid
        """
        logger.debug("Parsing bound from string: '%s'", s)
        # the order of iteration matters, weak inequality operators should be first.
        for op in [">=", "<=", "==", ">", "<"]:
            splits = s.split(op)
            if len(splits) == 2:
                bound = Bound(op, float(splits[-1]))  # type:ignore
                logger.debug("Parsed bound: %s", bound)
                return bound
        logger.error("Failed to parse bound from string: '%s'", s)
        raise ValueError("Invalid 'Bound' format")

    def __str__(self) -> str:
        return f"{self.operator}{self.value}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(operator='{self.operator}', value='{self.value}')"


__all__ = ["Bound"]
