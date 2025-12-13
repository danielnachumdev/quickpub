import logging
from typing import List, Optional, Dict, Callable
from danielutils import get_files

from .classifiers import Classifier
from .structures import Version, Dependency

logger = logging.getLogger(__name__)


def _format_classifiers_string(classifiers: List[Classifier]) -> str:
    classifiers_string = ",\n\t".join([f'"{str(c)}"' for c in classifiers])
    if len(classifiers_string) > 0:
        classifiers_string = f"\n\t{classifiers_string}\n"
    return classifiers_string


def _build_py_typed_section(name: str, src_folder_path: str) -> str:
    for file in get_files(src_folder_path):
        if file == "py.typed":
            logger.debug("Found py.typed file, adding package-data configuration")
            return f"""[tool.setuptools.package-data]
"{name}" = ["py.typed"]"""
    return ""


def _build_scripts_section(name: str, scripts: Dict[str, Callable]) -> str:
    logger.debug("Adding [project.scripts] section with %d entries", len(scripts))
    scripts_entries = []
    for script_name, func in scripts.items():
        module = func.__module__
        func_name = func.__name__
        if module == "__main__":
            module = f"{name}.__main__"
        entry_point = f"{module}:{func_name}"
        scripts_entries.append(f'    {script_name} = "{entry_point}"')
    return "\n[project.scripts]\n" + "\n".join(scripts_entries) + "\n"


def _build_toml_content(
    name: str,
    version: Version,
    author: str,
    author_email: str,
    description: str,
    readme_file_path: str,
    license_file_path: str,
    keywords: List[str],
    min_python: Version,
    dependencies: List[Dependency],
    classifiers_string: str,
    scripts_section: str,
    py_typed: str,
    homepage: str,
) -> str:
    return f"""[build-system]
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
classifiers = [{classifiers_string}]{scripts_section}
[tool.setuptools]
packages = ["{name}"]

{py_typed}

[project.urls]
"Homepage" = "{homepage}"
"Bug Tracker" = "{homepage}/issues"
"""


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
    classifiers: List[Classifier],
    scripts: Optional[Dict[str, Callable]] = None,
) -> None:
    logger.info("Creating pyproject.toml for package '%s' version '%s'", name, version)
    classifiers_string = _format_classifiers_string(classifiers)
    py_typed = _build_py_typed_section(name, src_folder_path)
    scripts_section = ""
    if scripts:
        scripts_section = _build_scripts_section(name, scripts)
    toml_content = _build_toml_content(
        name,
        version,
        author,
        author_email,
        description,
        readme_file_path,
        license_file_path,
        keywords,
        min_python,
        dependencies,
        classifiers_string,
        scripts_section,
        py_typed,
        homepage,
    )
    with open("pyproject.toml", "w", encoding="utf8") as f:
        f.write(toml_content)
    logger.info("Successfully created pyproject.toml")


def create_setup() -> None:
    logger.info("Creating setup.py file")
    with open("./setup.py", "w", encoding="utf8") as f:
        f.write("from setuptools import setup\n\nsetup()\n")
    logger.info("Successfully created setup.py")


def create_manifest(*, name: str) -> None:
    logger.info("Creating MANIFEST.in for package '%s'", name)
    with open("./MANIFEST.in", "w", encoding="utf8") as f:
        f.write(f"recursive-include {name} *.py")
    logger.info("Successfully created MANIFEST.in")


__all__ = ["create_setup", "create_toml"]
