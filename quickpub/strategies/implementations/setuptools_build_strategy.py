from danielutils import info

from ..build_strategy import BuildStrategy


class SetuptoolsBuildStrategy(BuildStrategy):
    def execute_strategy(self, *args, **kwargs) -> None:
        from quickpub.proxy import cm
        from quickpub.enforcers import exit_if
        if self.verbose:
            info("Creating new distribution...")
        ret, stdout, stderr = cm("python", "setup.py", "sdist")
        exit_if(
            ret != 0,
            stderr.decode(encoding="utf8")
        )


__all__ = [
    "SetuptoolsBuildStrategy",
]
