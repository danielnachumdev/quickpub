import re
from typing import Optional, List
from .quality_runner import QualityRunner


class MypyRunner(QualityRunner):
    def _build_command(self, target: str) -> str:
        command: str = self.get_executable()
        if self.has_config:
            command += f" --config-file {self.config_path}"
        command += f" {target}"
        return command

    RATING_PATTERN: re.Pattern = re.compile(
        "Found (\d+(?:\.\d+)?) errors in (\d+(?:\.\d+)?) files \(checked (\d+(?:\.\d+)?) source files\)")

    def __init__(self, bound: str = "<15", configuration_path: Optional[str] = None,
                 executable_path: Optional[str] = None) -> None:
        QualityRunner.__init__(self, name="mypy", bound=bound, configuration_path=configuration_path,
                               executable_path=executable_path)

    def _calculate_score(self, ret, lines: List[str], verbose: bool = False) -> float:
        from ...enforcers import exit_if
        rating_line = lines[-1]
        if rating_line.startswith("Success"):
            return 0.0
        exit_if(not (m := self.RATING_PATTERN.match(rating_line)),
                f"Failed running MyPy, got exit code {ret}. try running manually using:\n\t{self._build_command('TARGE')}",
                verbose=verbose)
        num_failed = float(m.group(1))
        active_files = float(m.group(2))
        total_files = float(m.group(3))
        return num_failed


__all__ = [
    'MypyRunner',
]
