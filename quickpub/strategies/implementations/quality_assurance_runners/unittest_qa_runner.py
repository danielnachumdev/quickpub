import re
import os
from typing import Optional, List
from danielutils import get_current_working_directory, set_current_working_directory, LayeredCommand, warning

from ...quality_assurance_runner import QualityAssuranceRunner


def _removesuffix(string: str, suffix: str) -> str:
    """Remove a suffix from a string.

    Replace this with str.removesuffix() from stdlib when minimum Python
    version is 3.9.
    """
    if suffix and string.endswith(suffix):
        return string[: -len(suffix)]
    return string


class UnittestRunner(QualityAssuranceRunner):
    NUM_TESTS_PATTERN: re.Pattern = re.compile(r"Ran (\d+) tests? in \d+\.\d+s")
    NUM_FAILED_PATTERN: re.Pattern = re.compile(r"FAILED \((?:failures=(\d+))?(?:, )?(?:errors=(\d+))?\)")

    def _install_dependencies(self, base: LayeredCommand) -> None:
        return None

    def _pre_command(self):
        self._cwd = get_current_working_directory()
        if self.target is None:
            self.target = ""
            warning("This is not supposed to happen. See quickpub's UnitestRunner._pre_command")
        set_current_working_directory(os.path.join(self._cwd, self.target))

    def _post_command(self):
        set_current_working_directory(self._cwd)

    def __init__(self, target: Optional[str] = "./tests", bound: str = ">=0.8", no_tests_score: float = 0) -> None:
        QualityAssuranceRunner.__init__(self, name="unittest", bound=bound, target=target)
        self._cwd = ""
        self.no_tests_score = no_tests_score

    def _build_command(self, src: str, *args, use_system_interpreter: bool = False) -> str:
        command: str = self.get_executable()
        rel = _removesuffix(os.path.relpath(src, self.target), src.lstrip("./\\"))
        command += f" discover -s {rel}"
        return command  # f"cd {self.target}; {command}"  # f"; cd {self.target}"

    def _calculate_score(self, ret: int, lines: List[str], *, verbose: bool = False) -> float:
        num_tests_ran_line = lines[-3]
        num_tests_failed_line = lines[-1]
        try:
            num_tests = int(self.NUM_TESTS_PATTERN.match(num_tests_ran_line).group(1))
            if num_tests == 0:
                return self.no_tests_score
            num_failed = 0
            num_errors = 0
            if num_tests_failed_line != "OK":
                m = self.NUM_FAILED_PATTERN.match(num_tests_failed_line)
                num_failed = int(m.group(1) or "0")
                num_errors = int(m.group(2) or "0")
            return 1 - ((num_failed + num_errors) / num_tests)

        except Exception as e:
            raise SystemExit(f"Failed running Unittest, got exit code {ret}. "
                             f"try running manually using: {self._build_command('TARGET')}") from e


__all__ = [
    'UnittestRunner',
]
