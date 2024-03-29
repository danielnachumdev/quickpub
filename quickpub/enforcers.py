import sys
from typing import Union, Callable

from danielutils import directory_exists, get_files, error, file_exists
from .structures import Version


def exit_if(predicate: Union[bool, Callable[[], bool]], msg: str) -> None:
    if isinstance(predicate, bool):
        if predicate:
            error(msg)
            sys.exit(1)
    else:
        if predicate():
            error(msg)
            sys.exit(1)


def enforce_correct_version(name: str, version: Version) -> None:
    if directory_exists("./dist"):
        max_version = Version(0, 0, 0)
        for d in get_files("./dist"):
            d = d.removeprefix(f"{name}-").removesuffix(".tar.gz")
            v = Version.from_str(d)
            max_version = max(max_version, v)
        exit_if(
            version <= max_version,
            f"Specified version is '{version}' but (locally available) latest existing is '{max_version}'"
        )


def enforce_pypirc_exists() -> None:
    exit_if(
        not file_exists("./.pypirc"),
        "No .pypirc file found"
    )


__all__ = [
    "enforce_correct_version",
    "enforce_pypirc_exists"
]
