import logging
import re
from typing import Optional, List

from danielutils import LayeredCommand

from ....enforcers import ExitEarlyError
from ...quality_assurance_runner import QualityAssuranceRunner

logger = logging.getLogger(__name__)


class PylintRunner(QualityAssuranceRunner):
    """Quality assurance runner for pylint code analysis. Scores based on pylint rating (0.0 to 10.0)."""

    def _install_dependencies(self, base: LayeredCommand) -> None:
        logger.info("Installing pylint dependencies")
        with base:
            base(self.package_manager.install_command("pylint"))

    RATING_PATTERN: re.Pattern = re.compile(r"([\d.]+)/([\d.]+)")

    def __init__(
        self,
        bound: str = ">=0.8",
        configuration_path: Optional[str] = None,
        executable_path: Optional[str] = None,
        package_manager=None,
    ) -> None:
        QualityAssuranceRunner.__init__(
            self,
            name="pylint",
            bound=bound,
            configuration_path=configuration_path,
            executable_path=executable_path,
            package_manager=package_manager,
        )
        logger.info(
            "Initialized PylintRunner with bound='%s', config='%s', executable='%s'",
            bound,
            configuration_path,
            executable_path,
        )

    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        command: str = self.get_executable()
        if self.has_config:
            command += f" --rcfile {self.config_path}"
        command += f" {target}"
        return command

    def _calculate_score(
        self, ret: int, lines: List[str], verbose: bool = False
    ) -> float:
        logger.debug("Calculating pylint score from analysis results")

        if len(lines) == 0:
            logger.debug("No pylint output, returning perfect score: 1.0")
            return 1

        for line in reversed(lines):
            match = self.RATING_PATTERN.search(line)
            if match:
                numerator = float(match.group(1))
                denominator = float(match.group(2))
                score = numerator / denominator
                logger.debug(
                    "Pylint score calculated: %.3f (%s/%s)",
                    score,
                    match.group(1),
                    match.group(2),
                )
                return score

        if ret == 0:
            return 1.0

        joined_output = "\n".join(lines)
        if ret == 1 and "parse-error" in joined_output:
            logger.debug(
                "Pylint reported parse-error with an empty target, returning perfect score: 1.0"
            )
            return 1.0

        if len(lines) == 1:
            if lines[0].endswith("No module named pylint"):
                logger.error("Pylint module not found")
                raise ExitEarlyError("No module named pylint found")

            if lines[0].startswith("The config file") and lines[0].endswith(
                "doesn't exist!"
            ):
                logger.error("Config file error: %s", lines[0])
                raise ExitEarlyError(lines[0])

            logger.error("Unexpected pylint error: %s", lines[0])
            raise ExitEarlyError(f"Got an unexpected error: {lines[0]}")

        msg = f"Failed running Pylint, got exit code {ret}. Try running manually using: {self._build_command('TARGET')}"
        logger.error("Failed to parse pylint rating from output: %s", joined_output)
        raise ExitEarlyError(msg)


__all__ = [
    "PylintRunner",
]
