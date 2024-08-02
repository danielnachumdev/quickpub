from unittest.mock import patch

from danielutils import AutoCWDTestCase, delete_directory, create_file, get_current_file_name, \
    get_current_working_directory, AlwaysTeardownTestCase

from quickpub import MypyRunner, DefaultPythonProvider, Bound

TEMP_VENV_NAME: str = "temp_clean_venv"
with open("./test_qa_runners/test_mypy_runner.py", "r") as f:
    CODE: str = f.read()

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
            bound="<15"
        )

    def tearDown(self):
        delete_directory(TEMP_VENV_NAME)

    @patch("quickpub.strategies.implementations.quality_assurance_runners.mypy_qa_runner.MypyRunner._build_command",
           return_value=f"..\\{TEMP_VENV_NAME}\\Scripts\\python.exe -m mypy .\\")
    def test_no_mypy(self, *args):
        with self.base:
            self.base(f"python -m venv {TEMP_VENV_NAME}")
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
        self.runner = MypyRunner(configuration_path="./mypy.ini", bound="<1")
        with self.base:
            self.runner.run(
                target="./",
                executor=self.base,
                print_func=print,
                env_name=self.env_name
            )

    def test_with_explicit_executable(self):
        create_file("__init__.py")
