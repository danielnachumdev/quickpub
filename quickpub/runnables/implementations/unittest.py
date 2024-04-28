import re
import os
from typing import Optional, List
from danielutils import get_current_working_directory, set_current_working_directory
from ..common_check import CommonCheck


class UnittestRunner(CommonCheck):
    def _pre_command(self):
        self._cwd = get_current_working_directory()
        set_current_working_directory(os.path.join(self._cwd, self.target))

    def _post_command(self):
        set_current_working_directory(self._cwd)

    RATING_PATTERN: re.Pattern = re.compile(r".*?([\d\.\/]+)")

    def __init__(self, target: Optional[str] = "./tests", bound: str = ">=0.8") -> None:
        CommonCheck.__init__(self, name="unittest", bound=bound, target=target)
        self._cwd = ""

    def _build_command(self, src: str, *args) -> str:
        command: str = self.get_executable()
        rel = os.path.relpath(src, self.target).removesuffix(src.lstrip("./\\"))
        command += f" discover -s {rel}"
        return command  # f"cd {self.target}; {command}"  # f"; cd {self.target}"

    def _calculate_score(self, ret: int, lines: List[str]) -> float:
        from ...enforcers import exit_if
        num_tests_line = lines[-3]
        num_failed_line = lines[-1] if lines[-1] != "OK" else "0"
        try:
            m = self.RATING_PATTERN.match(num_tests_line)
            if not m:
                raise AssertionError
            num_tests = m.group(1)
            m = self.RATING_PATTERN.match(num_failed_line)
            if not m:
                raise AssertionError
            num_failed = m.group(1)

            return 1.0 - (float(num_failed) / float(num_tests))
        except:
            exit_if(True,
                    f"Failed running Unittest, got exit code {ret}. try running manually using:\n\t{self._build_command('TARGET')}")


__all__ = [
    'UnittestRunner',
]
