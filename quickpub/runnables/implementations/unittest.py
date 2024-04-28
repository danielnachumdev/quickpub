import re
from typing import Optional
from ..common_check import CommonCheck


class UnittestRunner(CommonCheck):
    RATING_PATTERN: re.Pattern = re.compile(r".*?([\d\.\/]+)")

    def __init__(self) -> None:
        CommonCheck.__init__(self, "unittest", ">=0.8")

    def _build_command(self, *args) -> str:
        command: str = self.get_executable()
        command += f" discover"
        return command

    def _calculate_score(self, ret: int, lines: list[str]) -> float:
        from ...enforcers import exit_if
        rating_line = lines[-1]
        exit_if(not (m := self.RATING_PATTERN.match(rating_line)),
                f"Failed running MyPy, got exit code {ret}. try running manually using:\n\t{self._build_command()}")
        rating_string = m.group(1)
        return float(rating_string)


__all__ = [
    'UnittestRunner',
]
