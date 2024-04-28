from typing import List
from danielutils import get_files
from .custom_types import Path
from .classifiers import Classifier
from .structures import Version


def create_toml(
        *,
        name: str,
        src: Path,
        readme: Path,
        license: Path,
        version: Version,
        author: str,
        author_email: str,
        description: str,
        homepage: str,
        keywords: List[str],
        min_python: Version,
        dependencies: List[str],
        classifiers: List[Classifier]
) -> None:
    classifiers_string = ",\n\t".join([f"\"{str(c)}\"" for c in classifiers])
    if len(classifiers_string) > 0:
        classifiers_string = f"\n\t{classifiers_string}\n"
    py_typed = ""
    for file in get_files(src):
        if file == "py.typed":
            py_typed = f"""[tool.setuptools.package-data]
"{name}" = ["py.typed"]"""
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
dependencies = {dependencies}
keywords = {keywords}
license = {{ "file" = "{license}" }}
description = "{description}"
readme = {{file = "{readme}", content-type = "text/markdown"}}
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


def create_setup() -> None:
    with open("./setup.py", "w", encoding="utf8") as f:
        f.write("from setuptools import setup\n\nsetup()\n")


def create_manifest(*, name: str) -> None:
    with open("./MANIFEST.in", "w", encoding="utf8") as f:
        f.write(f"recursive-include {name} *.py")


__all__ = [
    "create_setup",
    "create_toml"
]
