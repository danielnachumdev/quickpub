from danielutils import info

from ..upload_target import UploadTarget

class GithubUploadTarget(UploadTarget):
    def execute_strategy(self, version: str, **kwargs) -> None:
        from quickpub.proxy import cm
        from quickpub.enforcers import exit_if
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
    "GithubUploadTarget",
]
