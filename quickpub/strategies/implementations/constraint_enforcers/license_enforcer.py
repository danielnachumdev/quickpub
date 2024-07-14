from danielutils import file_exists

from ...constraint_enforcer import ConstraintEnforcer


class LicenseEnforcer(ConstraintEnforcer):
    def __init__(self, path: str = "./LICENSE") -> None:
        self.path = path

    def enforce(self, **kwargs) -> None:
        if not file_exists(self.path):
            raise SystemExit(f"Could not find license file at '{self.path}'")


__all__ = [
    "LicenseEnforcer",
]
