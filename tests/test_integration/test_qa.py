import os
import sys
from typing import List
from unittest.mock import patch
from danielutils import create_file, delete_file, create_directory, delete_directory, chain_decorators, \
    get_caller_file_name, LayeredCommand, AutoCWDTestCase
import requests

from quickpub import publish, CondaPythonProvider, GithubUploadTarget, PypircUploadTarget, \
    SetuptoolsBuildSchema, QualityAssuranceRunner
from quickpub.qa import qa

PACKAGE_NAME: str = "foo"

PRINT_QUEUE: List[str] = []


class MockRunner(QualityAssuranceRunner):
    def _install_dependencies(self, base: LayeredCommand) -> None:
        return None

    def __init__(self) -> None:
        QualityAssuranceRunner.__init__(self, name="MockRunner", bound="<10", target=PACKAGE_NAME)

    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        return "echo $(python --version)"

    def _calculate_score(self, ret: int, command_output: List[str], *, verbose: bool = False) -> float:
        return 0

def _new_print(*args, sep: str = " ", end: str = "\n", file=sys.stdout, flush: bool = False) -> None:
    path = get_caller_file_name()
    if path is None:
        return
    caller_file = path.split("\\")[-1]
    if caller_file != "colors.py":
        file.write(sep.join(args) + end)
        if flush:
            file.flush()
        return
    PRINT_QUEUE.append(args)


class TestCondaPythonProvider(AutoCWDTestCase):

    def setUp(self):
        PRINT_QUEUE.clear()
        create_directory(PACKAGE_NAME)
        create_file(os.path.join(PACKAGE_NAME, "__init__.py"))

    def test_simplest_case_should_succeed(self, *args) -> None:
        qa(
            python_provider=CondaPythonProvider(["base"]),
            quality_assurance_strategies=[],
            package_name=PACKAGE_NAME,
            src_folder_path=f"./{PACKAGE_NAME}",
            dependencies=[]
        )

    def test_wrong_src_folder_path_should_fail(self, *args) -> None:
        qa(
            python_provider=CondaPythonProvider(["base"]),
            quality_assurance_strategies=[],
            package_name=PACKAGE_NAME,
            src_folder_path="./akjsbgfakjgbakls",
            dependencies=[]
        )

    @patch("builtins.print", _new_print)
    def test_non_existing_env_should_warn(self, *args):
        NON_EXISTENT_ENV_NAME: str = "sdjbnglksjdgnwkerjg"
        qa(
            python_provider=CondaPythonProvider([NON_EXISTENT_ENV_NAME]),
            quality_assurance_strategies=[],
            package_name=PACKAGE_NAME,
            dependencies=[],
            src_folder_path=f"./{NON_EXISTENT_ENV_NAME}"
        )
        self.assertListEqual(
            [
                ('\x1b[38;2;255;165;0mWARNING\x1b[0m: ',),
                (f"Couldn't find env '{NON_EXISTENT_ENV_NAME}'",)
            ],
            PRINT_QUEUE
        )
