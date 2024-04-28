import re
from typing import Optional
from danielutils.versioned_imports import t_list
from ..common_check import CommonCheck


class PylintRunner(CommonCheck):
    def __init__(self, configuration_path: Optional[str] = None, executable_path: Optional[str] = None) -> None:
        CommonCheck.__init__(self, "pylint", ">=0.8", configuration_path, executable_path)

    RATING_PATTERN: re.Pattern = re.compile(r".*?([\d\.\/]+)")

    def _calculate_score(self, ret: int, lines: t_list[str]) -> float:
        from ...enforcers import exit_if
        rating_line = lines[-2]
        exit_if(not (m := self.RATING_PATTERN.match(rating_line)),
                f"Failed running Pylint, got exit code {ret}. try running manually using:\n\t{self._build_command('TARGET')}")
        rating_string = m.group(1)  # type:ignore
        numerator, denominator = rating_string.split("/")
        return float(numerator) / float(denominator)


__all__ = [
    "PylintRunner",
]
