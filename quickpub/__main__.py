import argparse
from typing import Optional, Union, List, Any
from danielutils import warning, file_exists, error

from .strategies import BuildSchema, ConstraintEnforcer, UploadTarget, QualityAssuranceRunner, PythonProvider, \
    DefaultPythonProvider
from .validators import validate_version, validate_python_version, validate_keywords, validate_dependencies, \
    validate_source
from .structures import Version, Dependency
from .files import create_toml, create_setup, create_manifest
from .classifiers import *
from .qa import qa


def publish(
        *,
        name: str,
        author: str,
        author_email: str,
        description: str,
        homepage: str,

        build_schemas: List[BuildSchema],
        upload_targets: List[UploadTarget],
        enforcers: Optional[List[ConstraintEnforcer]] = None,
        global_quality_assurance_runners: Optional[List[QualityAssuranceRunner]] = None,
        python_interpreter_provider: PythonProvider = DefaultPythonProvider(),

        readme_file_path: str = "./README.md",
        license_file_path: str = "./LICENSE",
        version: Optional[Union[Version, str]] = None,
        min_python: Optional[Union[Version, str]] = None,
        dependencies: Optional[List[Union[str, Dependency]]] = None,
        keywords: Optional[List[str]] = None,
        explicit_src_folder_path: Optional[str] = None,

        demo: bool = False,
        config: Optional[Any] = None,
) -> None:
    """The main function for publishing a package. It performs all necessary steps to prepare and publish the package.

     :param name: The name of the package.
     :param author: The name of the author.
     :param author_email: The email of the author.
     :param description: A short description of the package.
     :param homepage: The homepage URL for the package (e.g., GitHub repository).
     :param global_quality_assurance_runners: Strategies for quality assurance. These will run on all Envs supplies by the supplier.
     :param build_schemas: Strategies for building the package.
     :param upload_targets: Strategies for uploading the package.
     :param python_interpreter_provider: Strategy for managing Python versions. Defaults to SystemInterpreter().
     :param explicit_src_folder_path: The path to the source code of the package. Defaults to <current working directory>/<name>.
     :param version: The version for the new distribution. Defaults to "0.0.1".
     :param readme_file_path: The path to the README file. Defaults to "./README.md".
     :param license_file_path: The path to the license file. Defaults to "./LICENSE".
     :param min_python: The minimum Python version required for the package. Defaults to the Python version running this script.
     :param keywords: A list of keywords describing areas of interest for the package. Defaults to None.
     :param dependencies: A list of dependencies for the package. Defaults to None.
     :param demo: Whether to perform checks without making any changes. Defaults to False.
     :param config: Reserved for future use. Defaults to None.

     Returns:
         None
     """
    version = validate_version(version)
    explicit_src_folder_path = validate_source(name, explicit_src_folder_path)
    if explicit_src_folder_path != f"./{name}":
        warning(
            "The source folder's name is different from the package's name. this may not be currently supported correctly")
    min_python = validate_python_version(min_python)  # type:ignore
    keywords = validate_keywords(keywords)
    validated_dependencies: List[Dependency] = validate_dependencies(dependencies)

    for enforcer in enforcers or []:
        enforcer.enforce(name=name, version=version, demo=demo)

    try:
        res = qa(
            python_interpreter_provider,
            global_quality_assurance_runners or [],
            name,
            explicit_src_folder_path,
            validated_dependencies
        )
        if not res:
            error(f"quickpub.publish exited early as '{name}' "
                  "did not pass quality assurance step, see above "
                  "logs to pass this step.")
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
        for schema in build_schemas:
            schema.build()
        for target in upload_targets:
            target.upload(name=name, version=version)


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


if __name__ == '__main__':
    print("CLI is not currently supported")
    # args = parse_args()
    #
    # publish(
    #     name=args.name,
    #     author=args.author,
    #     author_email=args.author_email,
    #     description=args.description,
    #     homepage=args.homepage,
    #     explicit_src_folder_path=args.explicit_src_folder_path,
    #     version=args.version,
    #     readme_file_path=args.readme_file_path,
    #     license_file_path=args.license_file_path,
    #     min_python=args.min_python,
    #     keywords=args.keywords,
    #     dependencies=args.dependencies,
    #     config=args.config
    # )
