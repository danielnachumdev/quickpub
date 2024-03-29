from typing import Optional, Union
from danielutils import warning, file_exists
from .validators import validate_version, validate_python_version, validate_keywords, validate_dependencies, \
    validate_source
from .functions import build, upload, commit, metrics
from .structures import Version, Config
from .files import create_toml, create_setup
from .classifiers import *
from .enforcers import enforce_correct_version, enforce_pypirc_exists, exit_if
from .custom_types import Path


def publish(
        *,
        name: str,
        author: str,
        author_email: str,
        description: str,
        homepage: str,
        src: Optional[Path] = None,
        version: Optional[Union[Version, str]] = None,
        readme: Path = "./README.md",
        license: Path = "./LICENSE",

        min_python: Optional[Union[Version, str]] = None,

        keywords: Optional[list[str]] = None,
        dependencies: Optional[list[str]] = None,
        config: Optional[Config] = None
) -> None:
    """The main function of this package. will do all the heavy lifting in order for you to publish your package.

    Args:
        name (str): The name of the package
        author (str): The name of the author
        author_email (str): The email of the author
        description (str): A short description for the package
        homepage (str): The homepage for the package. URL to the github repo is a good option.
        src (Optional[Path], optional): The path to the source code of the package. if None defaults to CWD/<name>
        version (Optional[Union[Version, str]], optional): The version to create the new distribution. if None defaults to 0.0.1
        readme (Path, optional): The path to the readme file. Defaults to "./README.md".
        license (Path, optional): The path to the license file . Defaults to "./LICENSE".
        min_python (Optional[Union[Version, str]], optional): The minimum version of python required for this package to run. Defaults to the version of python running this script.
        keywords (Optional[list[str]], optional): A list of keywords to describe areas of interests of this package. Defaults to None.
        dependencies (Optional[list[str]], optional): A list of the dependencies for this package. Defaults to None.
        config (Optional[Config], optional): reserved for future use. Defaults to None.
    """
    enforce_pypirc_exists()
    src = validate_source(name, src)
    if src != f"./{name}":
        warning(
            "The source folder's name is different from the package's name. this may not be currently supported correctly")
    exit_if(not file_exists(readme), f"Could not find readme file at {readme}")
    exit_if(not file_exists(license),
            f"Could not find license file at {license}")
    version = validate_version(version)
    enforce_correct_version(name, version)
    min_python = validate_python_version(min_python)
    keywords = validate_keywords(keywords)
    dependencies = validate_dependencies(dependencies)

    create_setup()
    create_toml(
        name=name,
        src=src,
        readme=readme,
        license=license,
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
