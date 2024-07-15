import unittest, sys
from typing import List
from unittest.mock import patch
from danielutils import create_file, delete_file, create_directory, delete_directory, chain_decorators, \
    get_caller_file_name, LayeredCommand
import requests

from quickpub import publish, CondaPythonProvider, GithubUploadTarget, PypircUploadTarget, \
    SetuptoolsBuildSchema, QualityAssuranceRunner
from utils import AutoCWDTestCase

PYPIRC = "./.pypirc"
PACAKGE = "pacakge"
README = "./README.md"
LICENSE = "./LICENSE"
MANIFEST = "./MANIFEST.in"


def f() -> None:
    publish(
        name=PACAKGE,
        version="0.0.1",
        author="danielnachumdev",
        author_email="danielnachumdev@gmail.com",
        description="A python package to quickly configure and publish a new package",
        homepage="https://github.com/danielnachumdev/quickpub",
        dependencies=["twine", "danielutils"]
    )


multipatch = chain_decorators(
    patch("quickpub.proxy.get", return_value=requests.Response()),
    patch("quickpub.proxy.cm", return_value=(0, b"", b"")),
    patch('quickpub.proxy.os_system', return_value=0)
)

PRINT_QUEUE: list = []


class MockRunner(QualityAssuranceRunner):
    def _install_dependencies(self, base: LayeredCommand) -> None:
        return None

    def __init__(self) -> None:
        QualityAssuranceRunner.__init__(self, name="MockRunner", bound="<10", target=PACAKGE)

    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        return "echo $(python --version)"

    def _calculate_score(self, ret: int, command_output: List[str], *, verbose: bool = False) -> float:
        return 0


class TestPythonManager(AutoCWDTestCase):
    def setUp(self):
        with open(PYPIRC, "w") as f:
            f.write("""[distutils]
index-servers =
    pypi
    testpypi

[pypi]
    username = __token__
    password = aaaaaaaaaaaaaaaaaaaaa

[testpypi]
    username = __token__
    password = aaaaaaaaaaaaaaaaaaaaaa""")
        create_directory(PACAKGE)
        create_file(README)
        create_file(LICENSE)
        global PRINT_QUEUE
        PRINT_QUEUE = []

    def tearDown(self):
        delete_file(PYPIRC)
        delete_directory(PACAKGE)
        delete_file(README)
        delete_file(LICENSE)
        delete_file(MANIFEST)
        delete_directory("dist")
        delete_directory(f"{PACAKGE}.egg-info")
        delete_file("setup.py")
        delete_file("pyproject.toml")

    @staticmethod
    def _new_print(*args, sep: str = " ", end: str = "\n", file=sys.stdout, flush: bool = False) -> None:
        caller_file = get_caller_file_name().split("\\")[-1]
        if caller_file != "colors.py":
            file.write(sep.join(args) + end)
            if flush:
                file.flush()
            return
        PRINT_QUEUE.append(args)

    @multipatch
    # @patch("danielutils.context_managers.temporary_file.TemporaryFile.read",
    #        return_value=[f"Found {51} errors in 7 files (checked 30 source files)\n"])
    # @patch("builtins.print", _new_print)
    def test_conda_python_manager(self, *args) -> None:
        publish(
            name=PACAKGE,
            version="0.0.1",
            author="danielnachumdev",
            author_email="danielnachumdev@gmail.com",
            description="A python package to quickly configure and publish a new package",
            homepage="https://github.com/danielnachumdev/quickpub",
            dependencies=["danielutils"],
            upload_targets=[PypircUploadTarget(), GithubUploadTarget()],
            build_schemas=[SetuptoolsBuildSchema()],
            python_interpreter_provider=CondaPythonProvider(["base", "390", "380"]),
            quality_assurance_runners=[MockRunner()]
        )
