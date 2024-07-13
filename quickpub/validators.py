from typing import Optional, Union, List

from danielutils import get_python_version

from .structures import Version, Dependency


def validate_version(version: Optional[Union[str, Version]] = None) -> Version:
    if version is None:
        return Version(0, 0, 1)
    return version if isinstance(version, Version) else Version.from_str(version)  # type: ignore


def validate_python_version(min_python: Optional[Version]) -> Version:
    if min_python is not None:
        return min_python
    return Version(*get_python_version())


def validate_keywords(keywords: Optional[List[str]]) -> List[str]:
    if keywords is None:
        return []
    return keywords


def validate_dependencies(dependencies: Optional[List[Union[str, Dependency]]]) -> List[Dependency]:
    if dependencies is None:
        return []
    res = []
    for dep in dependencies:
        if isinstance(dep, str):
            res.append(Dependency.from_string(dep))
        else:
            res.append(dep)
    return res


def validate_source(name: str, src: Optional[str] = None) -> str:
    if src is not None:
        return src
    return f"./{name}"


__all__ = [
    "validate_version",
    "validate_python_version",
    "validate_keywords",
    "validate_dependencies"
]
