import asyncio
import logging
import time
from typing import Optional, Union, List, Any, Dict, Callable

import fire
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
from .files import create_toml, create_setup, create_manifest
from .classifiers import *
from .qa import qa, SupportsProgress
from .logging_ import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


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
    # ========== QA Parameters ==========
    pbar: Optional[SupportsProgress] = None,  # tqdm
    demo: bool = False,
    config: Optional[Any] = None,
) -> None:
    """Publish a Python package by validating inputs, running quality assurance checks, creating package files, and building/uploading distributions.

    This function orchestrates the complete package publishing workflow:
    1. Validates package metadata (version, Python version, dependencies, keywords, source path)
    2. Runs constraint enforcers to ensure publishing requirements are met
    3. Executes quality assurance checks across specified Python environments
    4. Creates package configuration files (pyproject.toml, setup.py, MANIFEST.in)
    5. Builds distributions using provided build schemas
    6. Uploads distributions to specified targets

    Args:
        name: Package name (must match source folder name if using default path)
        author: Author name for package metadata
        author_email: Author email for package metadata
        description: Short description of the package
        homepage: Homepage URL (typically GitHub repository URL)
        build_schemas: List of build strategies to create package distributions
        upload_targets: List of upload strategies to publish distributions
        enforcers: Optional list of constraint enforcers to validate publishing requirements
        global_quality_assurance_runners: Optional list of QA runners to execute on all Python environments
        python_interpreter_provider: Strategy for managing Python versions (defaults to system Python)
        readme_file_path: Path to README file (defaults to "./README.md")
        license_file_path: Path to LICENSE file (defaults to "./LICENSE")
        version: Package version as Version object or string (defaults to "0.0.1" if not provided)
        min_python: Minimum required Python version (defaults to current Python version)
        dependencies: Optional list of dependencies as strings or Dependency objects
        keywords: Optional list of keywords describing the package
        explicit_src_folder_path: Optional explicit path to source code (defaults to "./{name}")
        scripts: Optional dictionary mapping script names to callable functions for entry points
        pbar: Optional progress bar object (e.g., tqdm instance) for tracking QA progress
        demo: If True, performs validation and file creation without building or uploading
        config: Reserved for future configuration options

    Raises:
        ExitEarlyError: If validation fails, constraint enforcement fails, or QA checks fail
        RuntimeError: If quality assurance stage encounters an unexpected error

    Returns:
        None
    """
    start_time = time.perf_counter()
    success = False
    try:
        version = validate_version(version)
        explicit_src_folder_path = validate_source(name, explicit_src_folder_path)
        if explicit_src_folder_path != f"./{name}":
            warning(
                "The source folder's name is different from the package's name. this may not be currently supported correctly"
            )
        min_python = validate_python_version(min_python)  # type:ignore
        keywords = validate_keywords(keywords)
        validated_dependencies: List[Dependency] = validate_dependencies(dependencies)
        for enforcer in enforcers or []:
            enforcer.enforce(name=name, version=version, demo=demo)
        try:
            res = asyncio.get_event_loop().run_until_complete(
                qa(
                    python_interpreter_provider,
                    global_quality_assurance_runners or [],
                    name,
                    explicit_src_folder_path,
                    validated_dependencies,
                    pbar,
                )
            )
            if not res:
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
        if not demo:
            for schema in build_schemas:
                schema.build()
            for target in upload_targets:
                target.upload(name=name, version=version)
        success = True
    finally:
        elapsed = time.perf_counter() - start_time
        logger.info("Publish finished in %.3fs (success=%s)", elapsed, success)


def main() -> None:
    fire.Fire(publish)


if __name__ == "__main__":
    main()

__all__ = ["main", "publish"]
