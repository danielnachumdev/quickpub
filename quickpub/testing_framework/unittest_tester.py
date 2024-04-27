from fractions import Fraction

from .tester import Tester


class UnittestTester(Tester):
    def run_tests(self) -> Fraction:
        assert False


__all__ = [
    "UnittestTester"
]
