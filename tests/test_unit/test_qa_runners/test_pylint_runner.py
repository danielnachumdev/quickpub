import os.path
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from quickpub import PylintRunner, DefaultPythonProvider, Bound, ExitEarlyError

from tests.base_test_classes import AsyncBaseTestClass
from tests.test_helpers import temporary_test_directory

TEMP_VENV_NAME: str = "temp_clean_venv"
CODE: str = """
from unittest.mock import patch

from danielutils import AutoCWDTestCase, AlwaysTeardownTestCase, LayeredCommand

from quickpub import MypyRunner

TEMP_VENV_NAME: str = "temp_clean_venv"
base: int = LayeredCommand()
runner = MypyRunner()


class TestMypyRunner(AutoCWDTestCase, AlwaysTeardownTestCase):
    @patch("quickpub.strategies.implementations.quality_assurance_runners.mypy_qa_runner.MypyRunner._build_command",
           return_value=f"..\\{TEMP_VENV_NAME}\\Scripts\\python.exe -m mypy .")
    def test_no_mypy(self, *args) -> int:
        with base:
            base(f"python -m venv {TEMP_VENV_NAME}")
            with self.assertRaises(SystemExit):
                runner.run(
                    target="./",
                    executor=base,
                )
"""
NUM_ERRORS: int = 8
CONFIG: str = """
[mypy]
strict = True
"""


class TestPylintRunner(AsyncBaseTestClass):
    async def _setup_provider(self):
        """Helper method to set up the Python provider."""
        async for name, base in DefaultPythonProvider():
            base.prev = None
            return name, base
        raise RuntimeError("No Python provider found")

    @patch(
        "quickpub.strategies.implementations.quality_assurance_runners.pylint_qa_runner.PylintRunner._build_command",
        return_value=f".\\{TEMP_VENV_NAME}\\Scripts\\python.exe -m pylint .\\",
    )
    async def test_no_pylint(self, *args):
        with temporary_test_directory() as tmp_dir:
            env_name, base = await self._setup_provider()
            with base:
                venv_path = tmp_dir / TEMP_VENV_NAME
                await base(f"{sys.executable} -m venv {venv_path}")
                runner = PylintRunner(
                    bound=f"<{NUM_ERRORS + 1}",
                    executable_path=str(venv_path / "Scripts" / "python.exe"),
                )
                with self.assertRaises(RuntimeError) as e:
                    await runner.run(
                        target=str(tmp_dir), executor=base, env_name=env_name
                    )
                self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_no_package(self):
        with temporary_test_directory() as tmp_dir:
            env_name, base = await self._setup_provider()
            runner = PylintRunner(bound=f"<{NUM_ERRORS + 1}")
            with base:
                await runner.run(target=str(tmp_dir), executor=base, env_name=env_name)

    async def test_empty_package(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            env_name, base = await self._setup_provider()
            runner = PylintRunner(bound=f"<{NUM_ERRORS + 1}")
            with base:
                await runner.run(target=str(tmp_dir), executor=base, env_name=env_name)

    async def test_bound_should_fail(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            (tmp_dir / "main.py").write_text(CODE)
            env_name, base = await self._setup_provider()
            runner = PylintRunner(bound=f"<{NUM_ERRORS + 1}")
            # Use a bound that will fail: require score > 1.0 (impossible since pylint scores are 0-1)
            runner.bound = Bound.from_string(">1.0")
            with base:
                with self.assertRaises(RuntimeError) as e:
                    await runner.run(
                        target=str(tmp_dir), executor=base, env_name=env_name
                    )
                self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_bound_should_succeed(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            (tmp_dir / "main.py").write_text(CODE)
            env_name, base = await self._setup_provider()
            runner = PylintRunner(bound=f"<{NUM_ERRORS + 1}")
            runner.bound = Bound("<", float("inf"))
            with base:
                await runner.run(target=str(tmp_dir), executor=base, env_name=env_name)

    async def test_with_config(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            (tmp_dir / "mypy.ini").write_text(CONFIG)
            (tmp_dir / "main.py").write_text(CODE)

            # Use absolute path to the .pylintrc file
            test_dir = Path(__file__).parent
            pylintrc_path = test_dir / ".pylintrc"
            env_name, base = await self._setup_provider()
            runner = PylintRunner(
                configuration_path=str(pylintrc_path),
                bound=f"<={NUM_ERRORS}",
            )
            with base:
                await runner.run(target=str(tmp_dir), executor=base, env_name=env_name)

    @patch("quickpub.strategies.quality_assurance_runner.file_exists")
    async def test_with_explicit_executable(self, mock_file_exists):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            (tmp_dir / "mypy.ini").write_text(CONFIG)
            (tmp_dir / "main.py").write_text(CODE)
            env_name, base = await self._setup_provider()
            exe_path = "\\".join(sys.executable.split("\\")[:-1]) + "\\pylint.exe"
            if "conda" in sys.executable:
                exe_path = exe_path.replace("pylint.exe", "Scripts\\pylint.exe")
            # Mock file_exists to return True for the executable path
            mock_file_exists.side_effect = lambda path: path == exe_path
            runner = PylintRunner(executable_path=exe_path, bound=f"<={NUM_ERRORS}")
            with base:
                await runner.run(target=str(tmp_dir), executor=base, env_name=env_name)
