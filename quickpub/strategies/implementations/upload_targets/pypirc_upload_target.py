import re

from danielutils import file_exists, info

from ..constraint_enforcers import PypircEnforcer
from ...upload_target import UploadTarget


class PypircUploadTarget(UploadTarget):
    REGEX_PATTERN: re.Pattern = PypircEnforcer.PYPIRC_REGEX

    def upload(self, name: str, version: str, **kwargs) -> None:  # type: ignore
        from quickpub.proxy import cm
        from quickpub.enforcers import exit_if
        self._validate_file_exists()
        self._validate_file_contents()
        if self.verbose:
            info("Uploading")
        ret, stdout, stderr = cm("twine", "upload", "--config-file", ".pypirc",
                                 f"dist/{name}-{version}.tar.gz")
        exit_if(
            ret != 0,
            f"Failed uploading the package to pypi. Try running the following command manually:\n\ttwine upload --config-file .pypirc dist/{name}-{version}.tar.gz"
        )

    def _validate_file_exists(self) -> None:
        if not file_exists(self.pypirc_file_path):
            raise RuntimeError(f"{self.__class__.__name__} can't find pypirc file at '{self.pypirc_file_path}'")

    def _validate_file_contents(self) -> None:
        with open(self.pypirc_file_path, "r", encoding="utf8") as f:
            text = f.read()
        if not self.REGEX_PATTERN.match(text):
            raise RuntimeError(
                f"{self.__class__.__name__} checked the contents of '{self.pypirc_file_path}' and it failed to match the following regex: r\"{self.REGEX_PATTERN.pattern}\"")

    def __init__(self, pypirc_file_path: str = "./.pypirc", verbose: bool = False) -> None:
        super().__init__(verbose)
        self.pypirc_file_path = pypirc_file_path


__all__ = [
    "PypircUploadTarget"
]
