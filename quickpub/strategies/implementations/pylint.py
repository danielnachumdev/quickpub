import re
from typing import Optional, List

from danielutils import LayeredCommand

from strategies.quality_assurance_strategy import QualityAssuranceStrategy


class PylintRunner(QualityAssuranceStrategy):
    def _install_dependencies(self, base: LayeredCommand) -> None:
        with base:
            base("pip install pylint")

    RATING_PATTERN: re.Pattern = re.compile(r".*?([\d\.\/]+)")

    def __init__(self, bound: str = ">=0.8", configuration_path: Optional[str] = None,
                 executable_path: Optional[str] = None) -> None:
        QualityAssuranceStrategy.__init__(self, name="pylint", bound=bound, configuration_path=configuration_path,
                                          executable_path=executable_path)

    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        command: str = self.get_executable()
        if self.has_config:
            command += f" --rcfile {self.config_path}"
        command += f" {target}"
        return command

    def _calculate_score(self, ret: int, lines: List[str], verbose: bool = False) -> float:
        from ...enforcers import exit_if
        if len(lines) == 1 and lines[0].endswith("No module named pylint"):
            raise RuntimeError("No module named pylint found")
        index = -2
        if lines[-1] == '\x1b[0m':
            index += -1
        rating_line = lines[index]
        m = self.RATING_PATTERN.match(rating_line)
        msg = f"Failed running Pylint, got exit code {ret}. Try running manually using: {self._build_command('TARGET')}"
        exit_if(not m, msg)
        rating_string = m.group(1)  # type:ignore
        numerator, denominator = rating_string.split("/")
        return float(numerator) / float(denominator)


__all__ = [
    "PylintRunner",
]
