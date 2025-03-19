import re
from typing import Optional, List

from danielutils import LayeredCommand

from ....enforcers import ExitEarlyError
from ...quality_assurance_runner import QualityAssuranceRunner


class MypyRunner(QualityAssuranceRunner):
    NO_TESTS_PATTERN: re.Pattern = re.compile(r"There are no \.py\[i\] files in directory '[\w\.\\\/]+'")
    RATING_PATTERN: re.Pattern = re.compile(
        r"Found (\d+(?:\.\d+)?) errors? in (\d+(?:\.\d+)?) files? \(checked (\d+(?:\.\d+)?) source files?\)")

    def _install_dependencies(self, base: LayeredCommand) -> None:
        with base:
            base("pip install mypy")

    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        command: str = self.get_executable(use_system_interpreter)
        if self.has_config:
            command += f" --config-file {self.config_path}"
        command += f" {target}"
        return command

    def __init__(self, bound: str = "<15", configuration_path: Optional[str] = None,
                 executable_path: Optional[str] = None) -> None:
        QualityAssuranceRunner.__init__(self, name="mypy", bound=bound, configuration_path=configuration_path,
                                        executable_path=executable_path)

    def _calculate_score(self, ret, lines: List[str], verbose: bool = False) -> float:
        from quickpub.enforcers import exit_if
        rating_line = lines[-1]
        if self.NO_TESTS_PATTERN.match(rating_line):
            return 0.0

        if rating_line.endswith("No module named mypy"):
            raise ExitEarlyError("Mypy is not installed.")

        if rating_line.startswith("mypy: error: Cannot find config file"):
            raise ExitEarlyError(rating_line)

        if rating_line.startswith("Success"):
            return 0.0

        exit_if(
            not (m := self.RATING_PATTERN.match(rating_line)),
            f"Failed running MyPy, got exit code {ret}. try running manually using: {self._build_command('TARGET')}",
            verbose=verbose,
            err_func=lambda msg: None  # TODO remove
        )
        num_failed = float(m.group(1))  # type :ignore
        # active_files = float(m.group(2))  # type :ignore
        # total_files = float(m.group(3))  # type :ignore
        return num_failed


__all__ = [
    'MypyRunner',
]
