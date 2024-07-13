from danielutils import info
from danielutils.university.oop.strategy import Strategy

from ..upload_strategy import UploadStrategy
from ...enforcers import exit_if
from ...proxy import cm


class GitUploadStrategy(UploadStrategy):
    def execute_strategy(self, version: str, **kwargs) -> None:
        if self.verbose:
            info("Git")
            info("\tStaging")
        ret, stdout, stderr = cm("git add .")
        exit_if(ret != 0, stderr.decode(encoding="utf8"))
        if self.verbose:
            info("\tCommitting")
        ret, stdout, stderr = cm(f"git commit -m \"updated to version {version}\"")
        exit_if(ret != 0, stderr.decode(encoding="utf8"))
        if self.verbose:
            info("\tPushing")
        ret, stdout, stderr = cm("git push")
        exit_if(ret != 0, stderr.decode(encoding="utf8"))


__all__ = [
    "GitUploadStrategy",
]
