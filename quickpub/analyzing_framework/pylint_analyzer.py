import re
from danielutils import file_exists, cm, info

from .analyzer import Analyzer


class PylintAnalyzer(Analyzer):
    RATING_PATTERN: re.Pattern = re.compile(r".*?([\d\.\/]+)")

    def analyze(self, target_path: str) -> float:
        from ..enforcers import exit_if
        command: str = f"{self.PYTHON} -m pylint"
        if self.use_executable:
            if not file_exists(self.executable_path):
                raise ValueError(f'{self.executable_path} does not exist')
            command = self.executable_path  # type:ignore

        if self.use_config_file:
            if not file_exists(self.config_file_path):
                raise ValueError(f'{self.config_file_path} does not exist')
            command += f" --rcfile {self.config_file_path}"

        command += f" {target_path}"
        info("Running Pylint")
        ret, out, err = cm(command)
        rating_line = out.decode("utf-8").splitlines()[-2]
        exit_if(not (m := self.RATING_PATTERN.match(rating_line)),
                f"Failed running Pylint, got exit code {ret}. try running manually using:\n\t{command}")
        rating_string = m.group(1)  # type:ignore
        numerator, denominator = rating_string.split("/")
        return float(numerator) / float(denominator)


__all__ = [
    "PylintAnalyzer",
]
