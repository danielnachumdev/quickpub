from danielutils import info

from ...enforcers import exit_if
from ...proxy import cm
from ..build_strategy import BuildStrategy


class SetuptoolsBuildStrategy(BuildStrategy):
    def execute_strategy(self, *args, **kwargs) -> None:
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
