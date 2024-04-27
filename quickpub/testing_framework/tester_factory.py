from typing import Literal, Optional

from .tester import Tester
from .unittest_tester import UnittestTester


class TesterFactory:
    @staticmethod
    def get_tester(name: Literal["unittest"], *, args: Optional[list] = None, kwargs: Optional[dict] = None) -> Tester:
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        if name == "unittest":
            return UnittestTester(*args, **kwargs)


__all__ = [
    'TesterFactory'
]
