import asyncio
import logging
import time
from typing import Optional, Union, List, Any, Dict, Callable, Tuple

import fire  # type: ignore[import-untyped]
from danielutils import warning, error

from quickpub import ExitEarlyError
from .strategies import (
    BuildSchema,
    ConstraintEnforcer,
    UploadTarget,
    QualityAssuranceRunner,
    PythonProvider,
    DefaultPythonProvider,
)
from .validators import (
    validate_version,
    validate_python_version,
    validate_keywords,
    validate_dependencies,
    validate_source,
)
from .structures import Version, Dependency
from .files import create_toml, create_setup, create_manifest, add_version_to_init
from .classifiers import *
from .qa import qa, SupportsProgress
from .logging_ import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def _validate_publish_inputs(
    name: str,
    version: Optional[Union[Version, str]],
    explicit_src_folder_path: Optional[str],
    min_python: Optional[Union[Version, str]],
    keywords: Optional[List[str]],
    dependencies: Optional[List[Union[str, Dependency]]],
) -> Tuple[Version, str, Version, List[str], List[Dependency]]:
    validated_version = validate_version(version)
    validated_src_path = validate_source(name, explicit_src_folder_path)
    if validated_src_path != f"./{name}":
        warning(
            "The source folder's name is different from the package's name. this may not be currently supported correctly"
        )
    converted_min_python: Optional[Version] = None
    if min_python is not None:
        converted_min_python = (
            min_python
            if isinstance(min_python, Version)
            else Version.from_str(min_python)
        )
    validated_min_python = validate_python_version(converted_min_python)
    validated_keywords = validate_keywords(keywords)
    validated_deps = validate_dependencies(dependencies)
    return (
        validated_version,
        validated_src_path,
        validated_min_python,
        validated_keywords,
        validated_deps,
    )


def _run_constraint_enforcers(
    enforcers: Optional[List[ConstraintEnforcer]],
    name: str,
    version: Version,
    demo: bool,
) -> None:
    for enforcer in enforcers or []:
        enforcer.enforce(name=name, version=version, demo=demo)


def _run_quality_assurance(
    python_interpreter_provider: PythonProvider,
    global_quality_assurance_runners: Optional[List[QualityAssuranceRunner]],
    name: str,
    explicit_src_folder_path: str,
    validated_dependencies: List[Dependency],
    pbar: Optional[SupportsProgress],
) -> None:
    try:
        result = asyncio.get_event_loop().run_until_complete(
            qa(
                python_interpreter_provider,
                global_quality_assurance_runners or [],
                name,
                explicit_src_folder_path,
                validated_dependencies,
                pbar,
            )
        )
        if not result:
            error(
                f"quickpub.publish exited early as '{name}' "
                "did not pass quality assurance step, see above "
                "logs to pass this step."
            )
            raise ExitEarlyError("QA step Failed")
    except ExitEarlyError as e:
        raise e
    except Exception as e:
        raise RuntimeError("Quality assurance stage has failed", e) from e


def _create_package_files(
    name: str,
    explicit_src_folder_path: str,
    readme_file_path: str,
    license_file_path: str,
    version: Version,
    author: str,
    author_email: str,
    description: str,
    homepage: str,
    keywords: List[str],
    validated_dependencies: List[Dependency],
    min_python: Version,
    scripts: Optional[Dict[str, Callable]],
) -> None:
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
            OperatingSystemClassifier.MicrosoftWindows,
        ],
        min_python=min_python,
        scripts=scripts,
    )
    create_manifest(name=name)
    add_version_to_init(
        name=name, src_folder_path=explicit_src_folder_path, version=version
    )


def _build_and_upload_packages(
    build_schemas: List[BuildSchema],
    upload_targets: List[UploadTarget],
    name: str,
    version: Version,
    demo: bool,
) -> None:
    if not demo:
        for schema in build_schemas:
            schema.build()
        for target in upload_targets:
            target.upload(name=name, version=version)


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
    scripts: Optional[Dict[str, Callable]] = None,
    pbar: Optional[SupportsProgress] = None,
    demo: bool = False,
    config: Optional[Any] = None,
) -> None:
    start_time = time.perf_counter()
    success = False
    try:
        (
            validated_version,
            validated_src_path,
            validated_min_python,
            validated_keywords,
            validated_deps,
        ) = _validate_publish_inputs(
            name, version, explicit_src_folder_path, min_python, keywords, dependencies
        )
        _run_constraint_enforcers(enforcers, name, validated_version, demo)
        _run_quality_assurance(
            python_interpreter_provider,
            global_quality_assurance_runners,
            name,
            validated_src_path,
            validated_deps,
            pbar,
        )
        _create_package_files(
            name,
            validated_src_path,
            readme_file_path,
            license_file_path,
            validated_version,
            author,
            author_email,
            description,
            homepage,
            validated_keywords,
            validated_deps,
            validated_min_python,
            scripts,
        )
        _build_and_upload_packages(
            build_schemas, upload_targets, name, validated_version, demo
        )
        success = True
    finally:
        elapsed = time.perf_counter() - start_time
        logger.info("Publish finished in %.3fs (success=%s)", elapsed, success)


def main() -> None:
    fire.Fire(publish)


if __name__ == "__main__":
    main()

__all__ = ["main", "publish"]
