import re
from typing import Optional, List

from danielutils import LayeredCommand

from ..base_runner import BaseRunner


class MypyRunner(BaseRunner):
    def _install_dependencies(self, base: LayeredCommand) -> None:
        with base:
            base("pip install pylint")

    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        command: str = self.get_executable(use_system_interpreter)
        if self.has_config:
            command += f" --config-file {self.config_path}"
        command += f" {target}"
        return command

    RATING_PATTERN: re.Pattern = re.compile(
        "Found (\d+(?:\.\d+)?) errors in (\d+(?:\.\d+)?) files \(checked (\d+(?:\.\d+)?) source files\)")

    def __init__(self, bound: str = "<15", configuration_path: Optional[str] = None,
                 executable_path: Optional[str] = None) -> None:
        BaseRunner.__init__(self, name="mypy", bound=bound, configuration_path=configuration_path,
                            executable_path=executable_path)

    def _calculate_score(self, ret, lines: List[str], verbose: bool = False) -> float:
        from ...enforcers import exit_if
        rating_line = lines[-1]
        if rating_line.startswith("Success"):
            return 0.0
        exit_if(not (m := self.RATING_PATTERN.match(rating_line)),
                f"Failed running MyPy, got exit code {ret}. try running manually using: {self._build_command('TARGET')}",
                verbose=verbose)
        num_failed = float(m.group(1))
        active_files = float(m.group(2))
        total_files = float(m.group(3))
        return num_failed


__all__ = [
    'MypyRunner',
]
