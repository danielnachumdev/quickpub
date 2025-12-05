import logging
from typing import Optional, Union, List

from danielutils import get_python_version

from .enforcers import ExitEarlyError
from .structures import Version, Dependency

logger = logging.getLogger(__name__)


def validate_version(version: Optional[Union[str, Version]] = None) -> Version:
    """
    Validate and convert version to Version object.

    :param version: Version string or Version object
    :return: Validated Version object
    :raises ExitEarlyError: If version is invalid or missing
    """
    logger.debug("Validating version: %s", version)
    if not bool(version):
        logger.error("Version validation failed: no version provided")
        raise ExitEarlyError(f"Must supply a version number. got '{version}'")

    if isinstance(version, Version):
        logger.debug("Version is already a Version object: %s", version)
        return version
    logger.debug("Converting string version to Version object: %s", version)
    return Version.from_str(version)  # type: ignore


def validate_python_version(min_python: Optional[Version]) -> Version:
    """
    Validate Python version requirement.

    :param min_python: Minimum Python version
    :return: Validated Python version
    """
    logger.debug("Validating Python version. min_python: %s", min_python)
    if min_python is not None:
        logger.debug("Using provided minimum Python version: %s", min_python)
        return min_python

    current_version = Version(*get_python_version())
    logger.debug("Using current Python version: %s", current_version)
    return current_version


def validate_keywords(keywords: Optional[List[str]]) -> List[str]:
    """
    Validate package keywords.

    :param keywords: List of keywords
    :return: Validated keywords list
    """
    logger.debug("Validating keywords: %s", keywords)
    if keywords is None:
        logger.debug("No keywords provided, returning empty list")
        return []
        logger.debug("Using provided keywords: %s", keywords)
    return keywords


def validate_dependencies(
    dependencies: Optional[List[Union[str, Dependency]]],
) -> List[Dependency]:
    """
    Validate and convert dependencies to Dependency objects.

    :param dependencies: List of dependency strings or Dependency objects
    :return: List of validated Dependency objects
    """
    logger.debug("Validating dependencies: %s", dependencies)
    if dependencies is None:
        logger.debug("No dependencies provided, returning empty list")
        return []

    res = []
    for dep in dependencies:
        if isinstance(dep, str):
            logger.debug("Converting string dependency to Dependency object: %s", dep)
            res.append(Dependency.from_string(dep))
        else:
            logger.debug("Using existing Dependency object: %s", dep)
            res.append(dep)

    logger.debug("Validated %d dependencies", len(res))
    return res


def validate_source(name: str, src: Optional[str] = None) -> str:
    """
    Validate source folder path.

    :param name: Package name
    :param src: Source folder path
    :return: Validated source path
    """
    logger.debug("Validating source for package '%s'. src: %s", name, src)
    if src is not None:
        logger.debug("Using provided source path: %s", src)
        return src

    default_src = f"./{name}"
    logger.debug("Using default source path: %s", default_src)
    return default_src


__all__ = [
    "validate_version",
    "validate_python_version",
    "validate_keywords",
    "validate_dependencies",
    "validate_source",
]
