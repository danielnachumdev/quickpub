import logging
import re
import subprocess
import sys
from typing import List, Union, Literal, Optional

from danielutils import LayeredCommand

from ....enforcers import ExitEarlyError
from ....structures import Bound
from ...quality_assurance_runner import QualityAssuranceRunner

logger = logging.getLogger(__name__)


class PytestRunner(QualityAssuranceRunner):
    """Quality assurance runner for pytest testing. Scores based on the ratio of passed tests to total tests."""

    PYTEST_SUMMARY_REGEX: re.Pattern = re.compile(
        r"=+ .*?in [\d\.]+s(?: \([^)]+\))? =+"
    )
    PYTEST_QUIET_SUMMARY_REGEX: re.Pattern = re.compile(
        r".*\d+ (?:failed|passed).+in [\d\.]+s(?: \([^)]+\))?"
    )
    PYTEST_FAILED_REGEX: re.Pattern = re.compile(r"(\d+) failed")
    PYTEST_PASSED_REGEX: re.Pattern = re.compile(r"(\d+) passed")
    PYTEST_SKIPPED_REGEX: re.Pattern = re.compile(r"(\d+) skipped")
    ANSI_ESCAPE_REGEX: re.Pattern = re.compile(r"\x1b\[[0-9;]*m")

    def __init__(
        self,
        *,
        bound: Union[str, Bound] = ">=0.8",
        target: str = "./tests",
        no_output_score: float = 0.0,
        no_tests_score: float = 1.0,
        xdist_workers: Union[int, Literal["auto"]] = "auto",
        configuration_path: Optional[str] = None,
        executable_path: Optional[str] = None,
        package_manager=None,
    ) -> None:
        super().__init__(
            name="pytest",
            bound=bound,
            target=target,
            configuration_path=configuration_path,
            executable_path=executable_path,
            package_manager=package_manager,
        )
        if not (0.0 <= no_tests_score <= 1.0):
            raise RuntimeError(
                "no_tests_score should be between 0.0 and 1.0 (including both)."
            )
        self.no_tests_score = no_tests_score

        if not (0.0 <= no_output_score <= 1.0):
            raise RuntimeError(
                "no_output_score should be between 0.0 and 1.0 (including both)."
            )
        self.no_output_score = no_output_score
        if isinstance(xdist_workers, int) and xdist_workers <= 0:
            raise RuntimeError("xdist_workers must be a positive integer or 'auto'.")
        if isinstance(xdist_workers, str) and xdist_workers != "auto":
            raise RuntimeError("xdist_workers must be a positive integer or 'auto'.")
        self.xdist_workers = xdist_workers

        logger.info(
            "Initialized PytestRunner with bound='%s', target='%s', no_tests_score=%s, no_output_score=%s",
            bound,
            target,
            no_tests_score,
            no_output_score,
        )

    def _is_xdist_installed(self) -> bool:
        try:
            result = subprocess.run(
                self.package_manager.show_command("pytest-xdist"),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            installed = result.returncode == 0
            logger.debug(
                "pytest-xdist availability check returned code %d (installed=%s)",
                result.returncode,
                installed,
            )
            return installed
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("pytest-xdist availability check failed: %s", exc)
            return False

    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        base_command = f"{sys.executable} -m pytest"
        if self.has_config:
            base_command += f" -c {self.config_path}"
        if self._is_xdist_installed():
            logger.debug("pytest-xdist detected; enabling distributed execution")
            return f"{base_command} -n {self.xdist_workers} {self.target}"
        logger.debug("pytest-xdist not detected; running without distribution")
        return f"{base_command} {self.target}"

    def _strip_ansi(self, text: str) -> str:
        return self.ANSI_ESCAPE_REGEX.sub("", text)

    def _is_summary_line(self, line: str) -> bool:
        cleaned = self._strip_ansi(line)
        return bool(
            self.PYTEST_SUMMARY_REGEX.match(cleaned)
            or self.PYTEST_QUIET_SUMMARY_REGEX.match(cleaned)
        )

    def _install_dependencies(self, base: LayeredCommand) -> None:
        logger.info("Installing pytest dependencies")
        with base:
            base(self.package_manager.install_command("pytest"))

    def _calculate_score(
        self, ret: int, command_output: List[str], *, verbose: bool = False
    ) -> float:
        logger.info("Calculating pytest score from test results")

        if len(command_output) == 0:
            logger.info(
                "No pytest output, returning no_output_score: %s", self.no_output_score
            )
            return self.no_output_score

        # Find the actual summary line by looking for the regex pattern
        # (pytest output may have warnings or other lines after the summary)
        rating_line = None
        for line in reversed(command_output):
            cleaned_line = self._strip_ansi(line)
            if "no tests ran" in cleaned_line.lower():
                logger.info(
                    "No tests ran, returning no_tests_score: %s", self.no_tests_score
                )
                return self.no_tests_score
            if self._is_summary_line(line):
                rating_line = cleaned_line
                break

        if rating_line is None:
            rating_line = self._strip_ansi(command_output[-1])
            if "no tests ran" in rating_line.lower():
                logger.info(
                    "No tests ran, returning no_tests_score: %s", self.no_tests_score
                )
                return self.no_tests_score

        if not (
            self.PYTEST_SUMMARY_REGEX.match(rating_line)
            or self.PYTEST_QUIET_SUMMARY_REGEX.match(rating_line)
        ):
            logger.error("Failed to parse pytest output: %s", rating_line)
            raise ExitEarlyError(
                f"Can't calculate score for pytest on the following line: {rating_line}"
            )

        failed_match = self.PYTEST_FAILED_REGEX.search(rating_line)
        passed_match = self.PYTEST_PASSED_REGEX.search(rating_line)
        skipped_match = self.PYTEST_SKIPPED_REGEX.search(rating_line)
        failed = int(failed_match.group(1)) if failed_match else 0
        passed = int(passed_match.group(1)) if passed_match else 0
        skipped = int(skipped_match.group(1)) if skipped_match else 0
        assert failed >= 0
        assert passed >= 0
        assert skipped >= 0

        total_tests = passed + failed + skipped
        if total_tests == 0:
            logger.info(
                "No test results found, returning no_tests_score: %s",
                self.no_tests_score,
            )
            return self.no_tests_score

        score = passed / total_tests
        logger.info(
            "Pytest score calculated: %.3f (passed: %d, failed: %d, skipped: %d)",
            score,
            passed,
            failed,
            skipped,
        )
        return score
