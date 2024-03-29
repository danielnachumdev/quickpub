from typing import Optional, Union
from danielutils import warning
from .validators import validate_version, validate_python_version, validate_keywords, validate_dependencies, \
    validate_source
from .publish import build, upload, commit, metrics
from .structures import Version, Config
from .files import create_toml, create_setup
from .classifiers import *
from .enforcers import enforce_correct_version, enforce_pypirc_exists
from .custom_types import Path


def publish(
        *,
        name: str,
        src: Optional[Path] = None,
        version: Optional[Union[Version, str]] = None,
        author: str,
        author_email: str,
        description: str,
        homepage: str,

        min_python: Optional[Union[Version, str]] = None,

        keywords: Optional[list[str]] = None,
        dependencies: Optional[list[str]] = None,
        config: Optional[Config] = None
) -> None:
    """

    :param name: The display name of the package
    :param src: The source folder of the package, Defaults to CWD/<name>
    :param version:
    :param author:
    :param author_email:
    :param description:
    :param homepage:
    :param min_python:
    :param keywords:
    :param dependencies:
    :param config:
    :return:
    """
    enforce_pypirc_exists()
    src = validate_source(name, src)
    if src != f"./{name}":
        warning(
            "The source folder's name is different from the package's name. this may not be currently supported correctly")
    version = validate_version(version)
    enforce_correct_version(name, version)
    min_python = validate_python_version(min_python)
    keywords = validate_keywords(keywords)
    dependencies = validate_dependencies(dependencies)

    create_setup()
    create_toml(
        name=name,
        src=src,
        version=version,
        author=author,
        author_email=author_email,
        description=description,
        homepage=homepage,
        keywords=keywords,
        dependencies=dependencies,
        classifiers=[
            DevelopmentStatusClassifier.Alpha,
            IntendedAudienceClassifier.Developers,
            ProgrammingLanguageClassifier.Python3,
            OperatingSystemClassifier.MicrosoftWindows
        ],
        min_python=min_python
    )

    build()
    upload(
        name=name,
        version=version
    )
    commit(
        version=version
    )
    metrics()

# if __name__ == '__main__':
#     publish()
