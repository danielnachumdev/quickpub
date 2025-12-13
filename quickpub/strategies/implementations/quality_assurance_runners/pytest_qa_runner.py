import logging
import re
import subprocess
import sys
from typing import List, Union

from danielutils import LayeredCommand

from ....enforcers import ExitEarlyError
from ....structures import Bound
from ...quality_assurance_runner import QualityAssuranceRunner

logger = logging.getLogger(__name__)


class PytestRunner(QualityAssuranceRunner):
    """Quality assurance runner for pytest testing. Scores based on the ratio of passed tests to total tests."""

    PYTEST_REGEX: re.Pattern = re.compile(
        r"=+ (?:(?P<failed>\d+) failed,? )?(?:(?P<passed>\d+) passed )?in [\d\.]+s =+"
    )

    def __init__(
        self,
        *,
        bound: Union[str, Bound] = ">=0.8",
        target: str = "./tests",
        no_output_score: float = 0.0,
        no_tests_score: float = 1.0,
        xdist_workers: Union[int, str] = "auto",
    ):
        super().__init__(name="pytest", bound=bound, target=target)
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

    @staticmethod
    def _is_xdist_installed() -> bool:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "pytest-xdist"],
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

    def _install_dependencies(self, base: LayeredCommand) -> None:
        logger.info("Installing pytest dependencies")
        with base:
            base(f"{sys.executable} -m pip install pytest")

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
            if "no tests ran" in line.lower():
                logger.info(
                    "No tests ran, returning no_tests_score: %s", self.no_tests_score
                )
                return self.no_tests_score
            if self.PYTEST_REGEX.match(line):
                rating_line = line
                break

        if rating_line is None:
            # Fallback to last line if no match found
            rating_line = command_output[-1]
            if "no tests ran" in rating_line.lower():
                logger.info(
                    "No tests ran, returning no_tests_score: %s", self.no_tests_score
                )
                return self.no_tests_score

        if not (m := self.PYTEST_REGEX.match(rating_line)):
            logger.error("Failed to parse pytest output: %s", rating_line)
            raise ExitEarlyError(
                f"Can't calculate score for pytest on the following line: {rating_line}"
            )

        dct = m.groupdict()
        failed = int(dct["failed"] or "0")
        passed = int(dct["passed"] or "0")
        assert failed >= 0
        assert passed >= 0

        if failed + passed == 0:
            logger.info(
                "No test results found, returning no_tests_score: %s",
                self.no_tests_score,
            )
            return self.no_tests_score

        score = passed / (passed + failed)
        logger.info(
            "Pytest score calculated: %.3f (passed: %d, failed: %d)",
            score,
            passed,
            failed,
        )
        return score
