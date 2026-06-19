"""Test helper utilities.

This module provides helper functions and context managers for tests,
including temporary directory management to replace AutoCWD functionality.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Set


def conda_is_available() -> bool:
    return shutil.which("conda") is not None


def list_conda_envs() -> Set[str]:
    if not conda_is_available():
        return set()
    result = subprocess.run(
        ["conda", "env", "list"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return set()
    return {
        line.split()[0]
        for line in result.stdout.splitlines()[2:]
        if line.split()
    }


def conda_base_env_available() -> bool:
    return "base" in list_conda_envs()


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
