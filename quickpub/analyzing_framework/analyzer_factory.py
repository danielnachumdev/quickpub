from typing import Literal, Optional

from .analyzer import Analyzer
from .mypy_analyzer import MyPyAnalyzer
from .pylint_analyzer import PylintAnalyzer


class AnalyzerFactory:
    @staticmethod
    def get_analyzer(name: Literal["mypy", "pylint"], *, args: Optional[list] = None,
                     kwargs: Optional[dict] = None) -> Analyzer:
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        if name == "mypy":
            return MyPyAnalyzer(*args, **kwargs)

        if name == "pylint":
            return PylintAnalyzer(*args, **kwargs)

        raise ValueError(f"Unrecognized analyzer name: {name}")


__all__ = [
    "AnalyzerFactory"
]
