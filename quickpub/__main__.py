from typing import Optional, Union
from danielutils import get_python_version
from .publish import build, upload, commit, metrics
from .structures import Version, Config
from .files import create_toml, create_setup
from .classifiers import *


def publish(
        *,
        name: str,
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
    if version is None:
        version: Version = None  # type: ignore
    else:
        version: Version = version if isinstance(version, Version) else Version.from_str(version)  # type: ignore

    if min_python is None:
        min_python = Version(*get_python_version())
    if keywords is None:
        keywords = []

    if dependencies is None:
        dependencies = []

    create_setup()
    create_toml(
        name=name,
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
