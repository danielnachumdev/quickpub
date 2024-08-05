import re

from danielutils import file_exists

from ...constraint_enforcer import ConstraintEnforcer


class PypircEnforcer(ConstraintEnforcer):
    PYPIRC_REGEX: re.Pattern = re.compile(
        r"\[distutils\]\nindex-servers =\n\s*pypi\n\s*testpypi\n\n\[pypi\]\n\s*username = __token__\n\s*password = .+\n\n\[testpypi\]\n\s*username = __token__\n\s*password = .+\n?")  # pylint: disable=line-too-long

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
                raise self.EXCEPTION_TYPE(f"Couldn't enforce '{self.path}'")


__all__ = [
    "PypircEnforcer",
]
