import os.path
import sys
from unittest.mock import patch

from danielutils import AutoCWDTestCase, delete_directory, create_file, get_current_file_name, \
    get_current_working_directory, AlwaysTeardownTestCase

from quickpub import MypyRunner, DefaultPythonProvider, Bound

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
                    print_func=print,
                )
"""
NUM_ERRORS: int = 8
CONFIG: str = """
[mypy]
strict = True
"""


class TestMypyRunner(AutoCWDTestCase, AlwaysTeardownTestCase):
    @classmethod
    def setUpClass(cls):
        cls.env_name, cls.base = next(iter(DefaultPythonProvider()))

    def setUp(self):
        self.runner = MypyRunner(
            bound=f"<{NUM_ERRORS + 1}"
        )

    def tearDown(self):
        delete_directory(TEMP_VENV_NAME)

    @patch("quickpub.strategies.implementations.quality_assurance_runners.mypy_qa_runner.MypyRunner._build_command",
           return_value=f"..\\{TEMP_VENV_NAME}\\Scripts\\python.exe -m mypy .\\")
    def test_no_mypy(self, *args):
        with self.base:
            self.base(f"{sys.executable} -m venv {TEMP_VENV_NAME}")
            self.runner = MypyRunner(
                bound=f"<{NUM_ERRORS + 1}",
                executable_path=os.path.join(TEMP_VENV_NAME, "Scripts", "python.exe"),
            )
            with self.assertRaises(SystemExit):
                self.runner.run(
                    target="./",
                    executor=self.base,
                    print_func=print,
                    env_name=self.env_name
                )

    def test_no_package(self):
        with self.base:
            self.runner.run(
                target="./",
                executor=self.base,
                print_func=print,
                env_name=self.env_name
            )

    def test_empty_package(self):
        create_file("__init__.py")
        with self.base:
            self.runner.run(
                target="./",
                executor=self.base,
                print_func=print,
                env_name=self.env_name
            )

    def test_bound_should_fail(self):
        create_file("__init__.py")
        with open("main.py", "w") as f:
            f.write(CODE)
        self.runner.bound = Bound.from_string("<=0")
        with self.base:
            with self.assertRaises(SystemExit):
                self.runner.run(
                    target="./",
                    executor=self.base,
                    print_func=print,
                    env_name=self.env_name
                )

    def test_bound_should_succeed(self):
        create_file("__init__.py")
        with open("main.py", "w") as f:
            f.write(CODE)
        self.runner.bound = Bound("<", float("inf"))
        with self.base:
            self.runner.run(
                target="./",
                executor=self.base,
                print_func=print,
                env_name=self.env_name
            )

    def test_with_config(self):
        create_file("__init__.py")
        with open("mypy.ini", "w") as f:
            f.write(CONFIG)
        with open("main.py", "w") as f:
            f.write(CODE)
        self.runner = MypyRunner(configuration_path="./mypy.ini", bound=f"<={NUM_ERRORS}")
        with self.base:
            self.runner.run(
                target="./",
                executor=self.base,
                print_func=print,
                env_name=self.env_name
            )

    def test_with_explicit_executable(self):
        create_file("__init__.py")
        with open("mypy.ini", "w") as f:
            f.write(CONFIG)
        with open("main.py", "w") as f:
            f.write(CODE)
        exe_path = "\\".join(sys.executable.split("\\")[:-1]) + "\\mypy.exe"
        if "conda" in sys.executable:
            exe_path = exe_path.replace("mypy.exe", "Scripts\\mypy.exe")
        self.runner = MypyRunner(executable_path=exe_path, bound=f"<={NUM_ERRORS}")
        with self.base:
            self.runner.run(
                target="./",
                executor=self.base,
                print_func=print,
                env_name=self.env_name
            )
