import re
from danielutils import file_exists, cm, info

from .analyzer import Analyzer


class MyPyAnalyzer(Analyzer):
    RATING_PATTERN: re.Pattern = re.compile(r".*?([\d\.\/]+)")

    def analyze(self, target_path: str) -> float:
        from ..enforcers import exit_if
        command: str = f"{self.PYTHON} -m mypy"
        if self.use_executable:
            if not file_exists(self.executable_path):
                raise ValueError(f'{self.executable_path} does not exist')
            command = self.executable_path

        if self.use_config_file:
            if not file_exists(self.config_file_path):
                raise ValueError(f'{self.config_file_path} does not exist')
            command += f" --config-file {self.config_file_path}"

        command += f" {target_path}"
        info("Running MyPy")
        ret, out, err = cm(command)
        rating_line = out.decode("utf-8").splitlines()[-1]
        exit_if(not (m := self.RATING_PATTERN.match(rating_line)),
                f"Failed running MyPy, got exit code {ret}. try running manually using:\n\t{command}")
        rating_string = m.group(1)
        return float(rating_string)


__all__ = [
    'MyPyAnalyzer',
]
