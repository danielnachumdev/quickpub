import sys
from danielutils import directory_exists, get_files, error
from .structures import Version


def enforce_correct_version(name: str, version: Version) -> None:
    if directory_exists("./dist"):
        max_version = Version(0, 0, 0)
        for d in get_files("./dist"):
            d = d.removeprefix(f"{name}-").removesuffix(".tar.gz")
            v = Version.from_str(d)
            max_version = max(max_version, v)
        if version < max_version:
            error(f"Specified version is '{version}' but (locally available) latest is '{max_version}'")
            sys.exit(1)
        if version == max_version:
            error(f"Version {version} already exists!")
            sys.exit(1)


__all__ = [
    "enforce_correct_version"
]
