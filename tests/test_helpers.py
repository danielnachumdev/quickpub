"""Test helper utilities.

This module provides helper functions and context managers for tests,
including temporary directory management to replace AutoCWD functionality.
"""

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


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
