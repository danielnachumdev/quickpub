import logging
from typing import List, Optional, Dict, Callable
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
    classifiers: List[Classifier],
    scripts: Optional[Dict[str, Callable]] = None,
) -> None:
    logger.info("Creating pyproject.toml for package '%s' version '%s'", name, version)
    classifiers_string = ",\n\t".join([f'"{str(c)}"' for c in classifiers])
    if len(classifiers_string) > 0:
        classifiers_string = f"\n\t{classifiers_string}\n"
    py_typed = ""
    for file in get_files(src_folder_path):
        if file == "py.typed":
            py_typed = f"""[tool.setuptools.package-data]
"{name}" = ["py.typed"]"""
            logger.debug("Found py.typed file, adding package-data configuration")
            break

    scripts_section = ""
    if scripts:
        logger.debug("Adding [project.scripts] section with %d entries", len(scripts))
        scripts_entries = []
        for script_name, func in scripts.items():
            module = func.__module__
            func_name = func.__name__
            # If module is __main__, prefix it with package name
            if module == "__main__":
                module = f"{name}.__main__"
            entry_point = f"{module}:{func_name}"
            scripts_entries.append(f'    {script_name} = "{entry_point}"')
        scripts_section = "\n[project.scripts]\n" + "\n".join(scripts_entries) + "\n"

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
classifiers = [{classifiers_string}]{scripts_section}
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
    logger.info("Creating MANIFEST.in for package '%s'", name)
    with open("./MANIFEST.in", "w", encoding="utf8") as f:
        f.write(f"recursive-include {name} *.py")
    logger.info("Successfully created MANIFEST.in")


__all__ = ["create_setup", "create_toml"]
