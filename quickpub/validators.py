import logging
from typing import Optional, Union, List

from danielutils import get_python_version

from .enforcers import ExitEarlyError
from .structures import Version, Dependency

logger = logging.getLogger(__name__)


def validate_version(version: Optional[Union[str, Version]] = None) -> Version:
    logger.debug(f"Validating version: {version}")
    if not bool(version):
        logger.error("Version validation failed: no version provided")
        raise ExitEarlyError(f"Must supply a version number. got '{version}'")

    if isinstance(version, Version):
        logger.debug(f"Version is already a Version object: {version}")
        return version
    logger.debug(f"Converting string version to Version object: {version}")
    return Version.from_str(version)  # type: ignore


def validate_python_version(min_python: Optional[Version]) -> Version:
    logger.debug(f"Validating Python version. min_python: {min_python}")
    if min_python is not None:
        logger.debug(f"Using provided minimum Python version: {min_python}")
        return min_python

    current_version = Version(*get_python_version())
    logger.debug(f"Using current Python version: {current_version}")
    return current_version


def validate_keywords(keywords: Optional[List[str]]) -> List[str]:
    logger.debug(f"Validating keywords: {keywords}")
    if keywords is None:
        logger.debug("No keywords provided, returning empty list")
        return []
    logger.debug(f"Using provided keywords: {keywords}")
    return keywords


def validate_dependencies(dependencies: Optional[List[Union[str, Dependency]]]) -> List[Dependency]:
    logger.debug(f"Validating dependencies: {dependencies}")
    if dependencies is None:
        logger.debug("No dependencies provided, returning empty list")
        return []

    res = []
    for dep in dependencies:
        if isinstance(dep, str):
            logger.debug(f"Converting string dependency to Dependency object: {dep}")
            res.append(Dependency.from_string(dep))
        else:
            logger.debug(f"Using existing Dependency object: {dep}")
            res.append(dep)

    logger.debug(f"Validated {len(res)} dependencies")
    return res


def validate_source(name: str, src: Optional[str] = None) -> str:
    logger.debug(f"Validating source for package '{name}'. src: {src}")
    if src is not None:
        logger.debug(f"Using provided source path: {src}")
        return src

    default_src = f"./{name}"
    logger.debug(f"Using default source path: {default_src}")
    return default_src


__all__ = [
    "validate_version",
    "validate_python_version",
    "validate_keywords",
    "validate_dependencies",
    "validate_source"
]
