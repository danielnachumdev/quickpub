import re
from typing import Optional, List
from ..common_check import CommonCheck


class PylintRunner(CommonCheck):
    RATING_PATTERN: re.Pattern = re.compile(r".*?([\d\.\/]+)")
    def __init__(self, bound: str = ">=0.8", configuration_path: Optional[str] = None,
                 executable_path: Optional[str] = None) -> None:
        CommonCheck.__init__(self, "pylint", bound, configuration_path, executable_path)

    def _build_command(self, target: str) -> str:
        command: str = self.get_executable()
        if self.has_config:
            command += f" --rcfile {self.config_path}"
        command += f" {target}"
        return command
    def _calculate_score(self, ret: int, lines: List[str]) -> float:
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
