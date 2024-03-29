from typing import Optional, Union, cast
from danielutils import error, get_python_version, get_files, directory_exists
from .publish import build, upload, commit, metrics
from .structures import Version, Config
from .files import create_toml, create_setup
from .classifiers import *
from .enforce_version import enforce_correct_version


def publish(
        *,
        name: str,
        src: str,
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
        version = Version(0, 0, 1)
    else:
        version: Version = version if isinstance(version, Version) else Version.from_str(version)  # type: ignore

    enforce_correct_version(name, version)

    if min_python is None:
        min_python = Version(*get_python_version())

    if keywords is None:
        keywords = []

    if dependencies is None:
        dependencies = []

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
