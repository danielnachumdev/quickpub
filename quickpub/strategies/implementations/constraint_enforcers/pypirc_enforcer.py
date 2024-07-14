import re

from danielutils import file_exists

from ...constraint_enforcer import ConstraintEnforcer


class PypircEnforcer(ConstraintEnforcer):
    PYPIRC_REGEX: re.Pattern = re.compile(
        r"\[distutils\]\nindex-servers =\n    pypi\n    testpypi\n\n\[pypi\]\n    username = __token__\n    password = .+\n\n\[testpypi\]\n    username = __token__\n    password = .+\n?")

    def __init__(self, path: str = "./.pypirc", should_enforce_expected_format: bool = True) -> None:
        self.path = path
        self.should_enforce_expected_format = should_enforce_expected_format

    def enforce(self, **kwargs) -> None:
        if not file_exists(self.path):
            raise SystemExit(f"Couldn't find '{self.path}'")
        if self.should_enforce_expected_format:
            with open(self.path, "r") as f:
                text = f.read()

            if not self.PYPIRC_REGEX.match(text):
                raise SystemExit(f"Couldn't enforce '{self.path}'")


__all__ = [
    "PypircEnforcer",
]
