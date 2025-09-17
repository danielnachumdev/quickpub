import logging
import re
from typing import Optional, List

from danielutils import LayeredCommand

from ....enforcers import ExitEarlyError
from ...quality_assurance_runner import QualityAssuranceRunner

logger = logging.getLogger(__name__)


class PylintRunner(QualityAssuranceRunner):
    def _install_dependencies(self, base: LayeredCommand) -> None:
        logger.info("Installing pylint dependencies")
        with base:
            base("pip install pylint")

    RATING_PATTERN: re.Pattern = re.compile(r".*?([\d\.\/]+)")

    def __init__(self, bound: str = ">=0.8", configuration_path: Optional[str] = None,
                 executable_path: Optional[str] = None) -> None:
        QualityAssuranceRunner.__init__(self, name="pylint", bound=bound, configuration_path=configuration_path,
                                        executable_path=executable_path)
        logger.info(f"Initialized PylintRunner with bound='{bound}', config='{configuration_path}', executable='{executable_path}'")

    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        command: str = self.get_executable()
        if self.has_config:
            command += f" --rcfile {self.config_path}"
        command += f" {target}"
        return command

    def _calculate_score(self, ret: int, lines: List[str], verbose: bool = False) -> float:
        from quickpub.enforcers import exit_if
        logger.info("Calculating pylint score from analysis results")
        
        if len(lines) == 0:
            logger.info("No pylint output, returning perfect score: 1.0")
            return 1
        if len(lines) == 1:
            if lines[0].endswith("No module named pylint"):
                logger.error("Pylint module not found")
                raise ExitEarlyError("No module named pylint found")

            if lines[0].startswith("The config file") and lines[0].endswith("doesn't exist!"):
                logger.error(f"Config file error: {lines[0]}")
                raise ExitEarlyError(lines[0])

            logger.error(f"Unexpected pylint error: {lines[0]}")
            raise ExitEarlyError(f"Got an unexpected error: {lines[0]}")
        
        index = -2
        if lines[-1] == '\x1b[0m':
            index += -1
        rating_line = lines[index]
        m = self.RATING_PATTERN.match(rating_line)
        msg = f"Failed running Pylint, got exit code {ret}. Try running manually using: {self._build_command('TARGET')}"
        exit_if(not m, msg)
        rating_string = m.group(1)  # type:ignore
        numerator, denominator = rating_string.split("/")
        score = float(numerator) / float(denominator)
        logger.info(f"Pylint score calculated: {score:.3f} ({numerator}/{denominator})")
        return score


__all__ = [
    "PylintRunner",
]
