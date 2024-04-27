from abc import abstractmethod, ABC
from fractions import Fraction


class Tester(ABC):
    @abstractmethod
    def run_tests(self) -> Fraction: ...


__all__ = [
    "Tester"
]
