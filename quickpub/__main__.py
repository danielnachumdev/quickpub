import argparse
from typing import Optional, Union, List
from danielutils import warning, file_exists, error

from .validators import validate_version, validate_python_version, validate_keywords, validate_dependencies, \
    validate_source
from .functions import build, upload, commit
from .structures import Version, AdditionalConfiguration, Dependency
from .files import create_toml, create_setup, create_manifest
from .classifiers import *
from .enforcers import enforce_local_correct_version, enforce_pypirc_exists, exit_if, enforce_remote_correct_version
from .qa import qa


def publish(
        *,
        name: str,
        author: str,
        author_email: str,
        description: str,
        homepage: str,
        explicit_src_folder_path: Optional[str] = None,
        version: Optional[Union[Version, str]] = None,
        readme_file_path: str = "./README.md",
        license_file_path: str = "./LICENSE",

        min_python: Optional[Union[Version, str]] = None,

        keywords: Optional[List[str]] = None,
        dependencies: Optional[List[Union[str, Dependency]]] = None,
        config: Optional[AdditionalConfiguration] = None,
        demo: bool = False
) -> None:
    """The main function of this package. will do all the heavy lifting in order for you to publish your package.

    Args:
        name (str): The name of the package
        author (str): The name of the author
        author_email (str): The email of the author
        description (str): A short description for the package
        homepage (str): The homepage for the package. URL to the github repo is a good option.
        explicit_src_folder_path (Optional[Path], optional): The path to the source code of the package. if None defaults to CWD/<name>
        version (Optional[Union[Version, str]], optional): The version to create the new distribution. if None defaults to 0.0.1
        readme_file_path (Path, optional): The path to the readme file. Defaults to "./README.md".
        license_file_path (Path, optional): The path to the license file . Defaults to "./LICENSE".
        min_python (Optional[Union[Version, str]], optional): The minimum version of python required for this package to run. Defaults to the version of python running this script.
        keywords (Optional[list[str]], optional): A list of keywords to describe areas of interests of this package. Defaults to None.
        dependencies (Optional[list[str]], optional): A list of the dependencies for this package. Defaults to None.
        config (Optional[Config], optional): reserved for future use. Defaults to None.
        :param demo: Whether to only perform checks without making any hard changes. Defaults to False.
    """
    enforce_pypirc_exists()
    explicit_src_folder_path = validate_source(name, explicit_src_folder_path)
    if explicit_src_folder_path != f"./{name}":
        warning(
            "The source folder's name is different from the package's name. this may not be currently supported correctly")
    exit_if(not file_exists(readme_file_path), f"Could not find readme file at {readme_file_path}")
    exit_if(not file_exists(license_file_path), f"Could not find license file at {license_file_path}")
    version = validate_version(version)
    if not demo:
        enforce_local_correct_version(name, version)
    min_python = validate_python_version(min_python)  # type:ignore
    keywords = validate_keywords(keywords)
    validated_dependencies: List[Dependency] = validate_dependencies(dependencies)
    enforce_remote_correct_version(name, version)

    try:
        if not qa(name, config, explicit_src_folder_path, validated_dependencies):
            error(
                f"quickpub.publish exited early as '{name}' did not pass quality assurance step, see above logs to pass this step.")
            raise SystemExit(1)
    except SystemExit as e:
        raise e
    except Exception as e:
        raise RuntimeError("Quality assurance stage has failed") from e

    create_setup()
    create_toml(
        name=name,
        src_folder_path=explicit_src_folder_path,
        readme_file_path=readme_file_path,
        license_file_path=license_file_path,
        version=version,
        author=author,
        author_email=author_email,
        description=description,
        homepage=homepage,
        keywords=keywords,
        dependencies=validated_dependencies,
        classifiers=[
            DevelopmentStatusClassifier.Alpha,
            IntendedAudienceClassifier.Developers,
            ProgrammingLanguageClassifier.Python3,
            OperatingSystemClassifier.MicrosoftWindows
        ],
        min_python=min_python
    )
    create_manifest(name=name)
    if not demo:
        build()
        upload(
            name=name,
            version=version
        )
        commit(
            version=version
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Publish a package")

    parser.add_argument('--name', required=True, type=str, help='Name of the package')
    parser.add_argument('--author', required=True, type=str, help='Author of the package')
    parser.add_argument('--author_email', required=True, type=str, help='Email of the author')
    parser.add_argument('--description', required=True, type=str, help='Description of the package')
    parser.add_argument('--homepage', required=True, type=str, help='Homepage of the package')
    parser.add_argument('--explicit_src_folder_path', type=str, help='Explicit source folder path')
    parser.add_argument('--version', type=str, help='Version of the package')
    parser.add_argument('--readme_file_path', type=str, default='./README.md', help='Path to the README file')
    parser.add_argument('--license_file_path', type=str, default='./LICENSE', help='Path to the LICENSE file')
    parser.add_argument('--min_python', type=str, help='Minimum Python version required')
    parser.add_argument('--keywords', nargs='*', help='Keywords for the package')
    parser.add_argument('--dependencies', nargs='*', help='Dependencies of the package')
    parser.add_argument('--config', help='Additional configuration for the package')

    return parser.parse_args()


def main():
    args = parse_args()

    publish(
        name=args.name,
        author=args.author,
        author_email=args.author_email,
        description=args.description,
        homepage=args.homepage,
        explicit_src_folder_path=args.explicit_src_folder_path,
        version=args.version,
        readme_file_path=args.readme_file_path,
        license_file_path=args.license_file_path,
        min_python=args.min_python,
        keywords=args.keywords,
        dependencies=args.dependencies,
        config=args.config
    )


if __name__ == '__main__':
    main()
