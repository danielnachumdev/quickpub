import unittest, sys
from unittest.mock import Mock, patch, MagicMock
from quickpub import publish, AdditionalConfiguration, MypyRunner, PylintRunner, UnittestRunner, CondaPythonManager
from danielutils import create_file, delete_file, create_directory, delete_directory, chain_decorators, \
    get_caller, get_caller_file_name
import requests

multipatch = chain_decorators(
    patch("quickpub.proxy.get", return_value=requests.Response()),
    patch("quickpub.proxy.cm", return_value=(0, b"", b"")),
    patch('quickpub.proxy.os_system', return_value=0)
)

PYPIRC = "./.pypirc"
PACAKGE = "pacakge"
README = "./README.md"
LICENSE = "./LICENSE"
MANIFEST = "./MANIFEST.in"
PRINT_QUEUE: list = []


class TestConfig(unittest.TestCase):
    def setUp(self):
        create_file(PYPIRC)
        create_directory(PACAKGE)
        create_file(README)
        create_file(LICENSE)
        PRINT_QUEUE.clear()

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

    @multipatch
    def test_no_arg(self, *args):
        publish(
            name=PACAKGE,
            version="0.0.1",
            author="danielnachumdev",
            author_email="danielnachumdev@gmail.com",
            description="A python package to quickly configure and publish a new package",
            homepage="https://github.com/danielnachumdev/quickpub",
            dependencies=["twine", "danielutils"],
        )

    @multipatch
    def test_explicit_none(self, *args):
        publish(
            name=PACAKGE,
            version="0.0.1",
            author="danielnachumdev",
            author_email="danielnachumdev@gmail.com",
            description="A python package to quickly configure and publish a new package",
            homepage="https://github.com/danielnachumdev/quickpub",
            dependencies=["twine", "danielutils"],
            config=None
        )

    @multipatch
    def tess_explicit_empty(self, *args):
        publish(
            name=PACAKGE,
            version="0.0.1",
            author="danielnachumdev",
            author_email="danielnachumdev@gmail.com",
            description="A python package to quickly configure and publish a new package",
            homepage="https://github.com/danielnachumdev/quickpub",
            dependencies=["twine", "danielutils"],
            config=AdditionalConfiguration()
        )

    @staticmethod
    def _new_print(*args, sep: str = " ", end: str = "\n", file=sys.stdout, flush: bool = False) -> None:
        special_case = get_caller().__name__ == "_write" and get_caller_file_name().split("\\")[
            -1] == "ascii_progress_bar.py"
        if not special_case:
            file.write(sep.join(args) + end)
            if flush:
                file.flush()
            return
        PRINT_QUEUE.append(args[0])

    @multipatch
    @patch("danielutils.print_.BetterPrinter.__call__", _new_print)
    def test_both(self, *args):
        name = f"{PACAKGE}/a.py"
        create_file(name)
        publish(
            name=PACAKGE,
            version="0.0.1",
            author="danielnachumdev",
            author_email="danielnachumdev@gmail.com",
            description="A python package to quickly configure and publish a new package",
            homepage="https://github.com/danielnachumdev/quickpub",
            dependencies=["twine", "danielutils"],
            config=AdditionalConfiguration(
                python_manager=CondaPythonManager(["base", "390", "380"]),
                runners=[
                    MypyRunner(bound="<15"),
                    PylintRunner(bound=">=0.8"),
                    UnittestRunner(bound=">=0.8"),
                ]
            )
        )
        delete_file(name)
        if len(PRINT_QUEUE) > 0:
            msg = '\n'.join(PRINT_QUEUE)
            self.fail(f"Some configurations failed:\n{msg}")
