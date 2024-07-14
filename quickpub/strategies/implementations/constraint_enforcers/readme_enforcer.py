from danielutils import file_exists

from ...constraint_enforcer import ConstraintEnforcer


class ReadmeEnforcer(ConstraintEnforcer):
    def __init__(self, path: str = "./README.md") -> None:
        self.path = path

    def enforce(self, **kwargs) -> None:
        if not file_exists(self.path):
            raise SystemExit(f"Could not find readme file at '{self.path}'")


__all__ = [
    "ReadmeEnforcer",
]
