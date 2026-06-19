from pathlib import Path
import os
import sys
from contextlib import contextmanager
from typing import Iterator

import pytest

PACKAGE_NAME = "samplepkg"
PACKAGE_VERSION = "1.0.0"


def write_mock_project(root: Path, *, with_uv_lock: bool) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text(
        f"""[project]
name = "{PACKAGE_NAME}"
version = "{PACKAGE_VERSION}"
requires-python = ">=3.8"
dependencies = []
""",
        encoding="utf-8",
    )
    package_dir = root / PACKAGE_NAME
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text(
        f'__version__ = "{PACKAGE_VERSION}"\n',
        encoding="utf-8",
    )
    if with_uv_lock:
        (root / "uv.lock").write_text("# mock uv lock\n", encoding="utf-8")
    return root


@contextmanager
def use_project_root(project_root: Path) -> Iterator[Path]:
    original_cwd = os.getcwd()
    original_path = sys.path.copy()
    os.chdir(project_root)
    sys.path.insert(0, str(project_root))
    try:
        yield project_root
    finally:
        os.chdir(original_cwd)
        sys.path[:] = original_path


@pytest.fixture
def mock_pip_project(tmp_path: Path) -> Path:
    return write_mock_project(tmp_path / "pip-project", with_uv_lock=False)


@pytest.fixture
def mock_uv_project(tmp_path: Path) -> Path:
    return write_mock_project(tmp_path / "uv-project", with_uv_lock=True)
