from typing import Optional, Union

from .validators import validate_version, validate_python_version, validate_keywords, validate_dependencies
from .publish import build, upload, commit, metrics
from .structures import Version, Config
from .files import create_toml, create_setup
from .classifiers import *
from .enforcers import enforce_correct_version, enforce_pypirc_exists
from .custom_types import Path


def publish(
        *,
        name: str,
        src: Path,
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
    enforce_pypirc_exists()
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
