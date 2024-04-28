import re
import os
from typing import Optional
from ..common_check import CommonCheck


class UnittestRunner(CommonCheck):
    RATING_PATTERN: re.Pattern = re.compile(r".*?([\d\.\/]+)")

    def __init__(self, target: Optional[str] = "./tests") -> None:
        CommonCheck.__init__(self, "unittest", ">=0.7", target)

    def _build_command(self, src: str, *args) -> str:
        command: str = self.get_executable()
        rel = os.path.relpath(src, self.target).removesuffix(src.lstrip("./\\"))
        command += f" discover -s {rel}"
        return command  # f"cd {self.target}; {command}"  # f"; cd {self.target}"

    def _calculate_score(self, ret: int, lines: list[str]) -> float:
        from ...enforcers import exit_if
        num_tests_line = lines[-3]
        num_failed_line = lines[-1]
        try:
            m = self.RATING_PATTERN.match(num_tests_line)
            if not m:
                raise AssertionError
            num_tests = m.group(1)
            m = self.RATING_PATTERN.match(num_failed_line)
            if not m:
                raise AssertionError
            num_failed = m.group(1)

            return 1 - (float(num_failed) / float(num_tests))
        except:
            exit_if(True,
                    f"Failed running Unittest, got exit code {ret}. try running manually using:\n\t{self._build_command('TARGET')}")


__all__ = [
    'UnittestRunner',
]
