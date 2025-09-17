import logging
import re
import os
from pathlib import Path
from typing import Optional, List
from danielutils import get_current_working_directory, set_current_working_directory, LayeredCommand, warning

from ....enforcers import ExitEarlyError
from ...quality_assurance_runner import QualityAssuranceRunner

logger = logging.getLogger(__name__)


def _removesuffix(string: str, suffix: str) -> str:
    """Remove a suffix from a string.

    Replace this with str.removesuffix() from stdlib when minimum Python
    version is 3.9.
    """
    if suffix and string.endswith(suffix):
        return string[: -len(suffix)]
    return string


class UnittestRunner(QualityAssuranceRunner):
    """Quality assurance runner for unittest testing."""
    NUM_TESTS_PATTERN: re.Pattern = re.compile(r"Ran (\d+) tests? in \d+\.\d+s")
    NUM_FAILED_PATTERN: re.Pattern = re.compile(
        r"FAILED \((?:failures=(\d+))?(?:, )?(?:errors=(\d+))?(?:, )?(?:skipped=(\d+))?\)|"
        r"FAILED \((?:errors=(\d+))?(?:, )?(?:failures=(\d+))?(?:, )?(?:skipped=(\d+))?\)|"
        r"FAILED \((?:skipped=(\d+))?(?:, )?(?:failures=(\d+))?(?:, )?(?:errors=(\d+))?\)")

    def _install_dependencies(self, base: LayeredCommand) -> None:
        return None

    def _pre_command(self) -> None:
        pass

    def _post_command(self):
        pass
        # set_current_working_directory(self._cwd)

    def __init__(self, target: Optional[str] = "./tests", bound: str = ">=0.8", no_tests_score: float = 0) -> None:
        QualityAssuranceRunner.__init__(self, name="unittest", bound=bound, target=target)
        self.no_tests_score = no_tests_score
        logger.info("Initialized UnittestRunner with target='%s', bound='%s', no_tests_score=%s", target, bound,
                    no_tests_score)

    def _build_command(self, src: str, *args, use_system_interpreter: bool = False) -> str:
        command: str = self.get_executable()
        rel = _removesuffix(os.path.relpath(src, self.target), src.lstrip("./\\"))
        command += f" discover -s {rel}"
        normalized_target_path = Path(os.path.join(os.getcwd(), self.target)).resolve()
        return f"cd {normalized_target_path} & {command} & cd {Path(os.getcwd()).resolve()}"  # This is for concurrency reasons

    def _calculate_score(self, ret: int, lines: List[str], *, verbose: bool = False) -> float:
        logger.info("Calculating unittest score from test results")

        try:
            num_tests_ran_line = lines[-3]
            num_tests_failed_line = lines[-1]
            num_tests = int(self.NUM_TESTS_PATTERN.match(num_tests_ran_line).group(1))
            if num_tests == 0:
                logger.info("No tests found, returning no_tests_score: %s", self.no_tests_score)
                return self.no_tests_score

            num_failed = 0
            num_errors = 0
            if num_tests_failed_line != "OK":
                if num_tests_failed_line.startswith("FAILED"):
                    m = self.NUM_FAILED_PATTERN.match(num_tests_failed_line)
                    if m:
                        # Handle different group positions based on the pattern that matched
                        groups = m.groups()
                        if groups[0] is not None:  # failures= first pattern
                            num_failed = int(groups[0] or "0")
                            num_errors = int(groups[1] or "0")
                        elif groups[3] is not None:  # errors= first pattern
                            num_failed = int(groups[4] or "0")
                            num_errors = int(groups[3] or "0")
                        elif groups[6] is not None:  # skipped= first pattern
                            num_failed = int(groups[7] or "0")
                            num_errors = int(groups[8] or "0")
                        else:
                            # Fallback to original logic if no groups match
                            num_failed = int(m.group(1) or "0")
                            num_errors = int(m.group(2) or "0")
                    else:
                        # If regex doesn't match, treat as malformed
                        raise ValueError(f"Failed to parse FAILED line: {num_tests_failed_line}")
                elif num_tests_failed_line.startswith("OK"):
                    # 'OK (skipped=3)' could it also be other stuff?
                    pass

            score = 1 - ((num_failed + num_errors) / num_tests)
            logger.info("Unittest score calculated: %.3f (tests: %d, failed: %d, errors: %d)", score, num_tests,
                        num_failed, num_errors)
            return score

        except Exception as e:
            logger.error("Failed to calculate unittest score: %s", e)
            raise ExitEarlyError(f"Failed running Unittest, got exit code {ret}. "
                                 f"try running manually using: {self._build_command('TARGET')}") from e


__all__ = [
    'UnittestRunner',
]
