import re
from typing import Optional
from danielutils.versioned_imports import t_list
from ..common_check import CommonCheck


class MypyRunner(CommonCheck):
    RATING_PATTERN: re.Pattern = re.compile(r".*?([\d\.\/]+)")

    def __init__(self, bound: str = "<15", configuration_path: Optional[str] = None,
                 executable_path: Optional[str] = None) -> None:
        CommonCheck.__init__(self, "mypy", bound, configuration_path, executable_path)

    def _calculate_score(self, ret, lines: t_list[str]) -> float:
        from ...enforcers import exit_if
        rating_line = lines[-1]
        exit_if(not (m := self.RATING_PATTERN.match(rating_line)),
                f"Failed running MyPy, got exit code {ret}. try running manually using:\n\t{self._build_command('TARGE')}")
        rating_string = m.group(1)
        return float(rating_string)


__all__ = [
    'MypyRunner',
]
