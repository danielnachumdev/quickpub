import os.path
import sys
import unittest
from unittest.mock import patch

from danielutils import (
    AutoCWDTestCase,
    delete_directory,
    create_file,
    AlwaysTeardownTestCase,
    AsyncAutoCWDTestCase,
    AsyncAlwaysTeardownTestCase,
)

from quickpub import PylintRunner, DefaultPythonProvider, Bound, ExitEarlyError

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
           return_value=f"..\{TEMP_VENV_NAME}\Scripts\python.exe -m mypy .")
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


class TestPylintRunner(AsyncAutoCWDTestCase, AsyncAlwaysTeardownTestCase):

    async def asyncSetUp(self):
        async for name, base in DefaultPythonProvider():
            base.prev = None
            self.env_name, self.base = name, base
            break
        self.runner = PylintRunner(bound=f"<{NUM_ERRORS + 1}")

    async def asyncTearDown(self):
        delete_directory(TEMP_VENV_NAME)

    @patch(
        "quickpub.strategies.implementations.quality_assurance_runners.pylint_qa_runner.PylintRunner._build_command",
        return_value=f".\\{TEMP_VENV_NAME}\\Scripts\\python.exe -m pylint .\\",
    )
    async def test_no_pylint(self, *args):
        with self.base:
            await self.base(f"{sys.executable} -m venv {TEMP_VENV_NAME}")
            self.runner = PylintRunner(
                bound=f"<{NUM_ERRORS + 1}",
                executable_path=os.path.join(TEMP_VENV_NAME, "Scripts", "python.exe"),
            )
            with self.assertRaises(RuntimeError) as e:
                await self.runner.run(
                    target="./", executor=self.base, env_name=self.env_name
                )
            self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_no_package(self):
        with self.base:
            await self.runner.run(
                target="./", executor=self.base, env_name=self.env_name
            )

    async def test_empty_package(self):
        create_file("__init__.py")
        with self.base:
            await self.runner.run(
                target="./", executor=self.base, env_name=self.env_name
            )

    async def test_bound_should_fail(self):
        create_file("__init__.py")
        with open("main.py", "w") as f:
            f.write(CODE)
        self.runner.bound = Bound.from_string("<=0")
        with self.base:
            with self.assertRaises(RuntimeError) as e:
                await self.runner.run(
                    target="./", executor=self.base, env_name=self.env_name
                )
            self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_bound_should_succeed(self):
        create_file("__init__.py")
        with open("main.py", "w") as f:
            f.write(CODE)
        self.runner.bound = Bound("<", float("inf"))
        with self.base:
            await self.runner.run(
                target="./", executor=self.base, env_name=self.env_name
            )

    async def test_with_config(self):
        import os
        from pathlib import Path

        create_file("__init__.py")
        with open("mypy.ini", "w") as f:
            f.write(CONFIG)
        with open("main.py", "w") as f:
            f.write(CODE)

        # Use absolute path to the .pylintrc file
        test_dir = Path(__file__).parent
        pylintrc_path = test_dir / ".pylintrc"
        self.runner = PylintRunner(
            configuration_path=str(pylintrc_path),
            bound=f"<={NUM_ERRORS}",
        )
        with self.base:
            await self.runner.run(
                target="./", executor=self.base, env_name=self.env_name
            )

    async def test_with_explicit_executable(self):
        create_file("__init__.py")
        with open("mypy.ini", "w") as f:
            f.write(CONFIG)
        with open("main.py", "w") as f:
            f.write(CODE)
        exe_path = "\\".join(sys.executable.split("\\")[:-1]) + "\\pylint.exe"
        if "conda" in sys.executable:
            exe_path = exe_path.replace("pylint.exe", "Scripts\\pylint.exe")
        self.runner = PylintRunner(executable_path=exe_path, bound=f"<={NUM_ERRORS}")
        with self.base:
            await self.runner.run(
                target="./", executor=self.base, env_name=self.env_name
            )
