"""Test helper utilities.

This module provides helper functions and context managers for tests,
including temporary directory management to replace AutoCWD functionality.
"""

import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def venv_python_executable(venv_path: Path) -> Path:
    if os.name == "nt":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def resolve_tool_executable(tool_name: str) -> str:
    found = shutil.which(tool_name)
    if found:
        return found
    if os.name == "nt":
        base = Path(sys.executable).parent
        if "conda" in sys.executable:
            return str(base / "Scripts" / f"{tool_name}.exe")
        return str(base / f"{tool_name}.exe")
    return str(Path(sys.executable).parent / tool_name)


@contextmanager
def temporary_test_directory(change_cwd: bool = True) -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        if change_cwd:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmp_dir)
                yield tmp_path
            finally:
                os.chdir(original_cwd)
        else:
            yield tmp_path
