import logging
from typing import List
from danielutils import get_files

from .classifiers import Classifier
from .structures import Version, Dependency

logger = logging.getLogger(__name__)


def create_toml(
        *,
        name: str,
        src_folder_path: str,
        readme_file_path: str,
        license_file_path: str,
        version: Version,
        author: str,
        author_email: str,
        description: str,
        homepage: str,
        keywords: List[str],
        min_python: Version,
        dependencies: List[Dependency],
        classifiers: List[Classifier]
) -> None:
    logger.info(f"Creating pyproject.toml for package '{name}' version '{version}'")
    classifiers_string = ",\n\t".join([f"\"{str(c)}\"" for c in classifiers])
    if len(classifiers_string) > 0:
        classifiers_string = f"\n\t{classifiers_string}\n"
    py_typed = ""
    for file in get_files(src_folder_path):
        if file == "py.typed":
            py_typed = f"""[tool.setuptools.package-data]
"{name}" = ["py.typed"]"""
            logger.debug("Found py.typed file, adding package-data configuration")
            break

    s = f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "{version}"
authors = [
    {{ name = "{author}", email = "{author_email}" }},
]
dependencies = {[str(dep) for dep in dependencies]}
keywords = {keywords}
license = {{ "file" = "{license_file_path}" }}
description = "{description}"
readme = {{file = "{readme_file_path}", content-type = "text/markdown"}}
requires-python = ">={min_python}"
classifiers = [{classifiers_string}]

[tool.setuptools]
packages = ["{name}"]
{py_typed}

[project.urls]
"Homepage" = "{homepage}"
"Bug Tracker" = "{homepage}/issues"
"""
    with open("pyproject.toml", "w", encoding="utf8") as f:
        f.write(s)
    logger.info("Successfully created pyproject.toml")


def create_setup() -> None:
    logger.info("Creating setup.py file")
    with open("./setup.py", "w", encoding="utf8") as f:
        f.write("from setuptools import setup\n\nsetup()\n")
    logger.info("Successfully created setup.py")


def create_manifest(*, name: str) -> None:
    logger.info(f"Creating MANIFEST.in for package '{name}'")
    with open("./MANIFEST.in", "w", encoding="utf8") as f:
        f.write(f"recursive-include {name} *.py")
    logger.info("Successfully created MANIFEST.in")


__all__ = [
    "create_setup",
    "create_toml"
]
