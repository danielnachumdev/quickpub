from typing import Optional, Union

from danielutils import get_python_version
from danielutils.versioned_imports import t_list
from .custom_types import Path
from .structures import Version


def validate_version(version: Optional[Union[str, Version]]) -> Version:
    if version is None:
        version = Version(0, 0, 1)
    else:
        version: Version = version if isinstance(version, Version) else Version.from_str(version)  # type: ignore
    return version


def validate_python_version(min_python: Optional[Version]) -> Version:
    if min_python is not None:
        return min_python
    return Version(*get_python_version())


def validate_keywords(keywords: Optional[t_list[str]]) -> t_list[str]:
    if keywords is None:
        return []
    return keywords


def validate_dependencies(dependencies: Optional[t_list[str]]) -> t_list[str]:
    if dependencies is None:
        return []
    return dependencies


def validate_source(name: str, src: Optional[Path] = None) -> Path:
    if src is not None:
        return src
    return f"./{name}"


__all__ = [
    "validate_version",
    "validate_python_version",
    "validate_keywords",
    "validate_dependencies"
]
