import builtins
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from quickpub import publish, AdditionalConfiguration, MypyRunner
from danielutils import create_file, delete_file, create_directory, delete_directory, chain_decorators, \
    get_caller_file_name

import requests

multipatch = chain_decorators(
    patch("quickpub.proxy.get", return_value=requests.Response()),
    patch("quickpub.proxy.cm", return_value=(0, b"", b"")),
    patch('quickpub.proxy.os_system', return_value=0),
)

PYPIRC = "./.pypirc"
PACAKGE = "pacakge"
README = "./README.md"
LICENSE = "./LICENSE"
MANIFEST = "./MANIFEST.in"
PRINT_QUEUE: list = []


class TestRunners(unittest.TestCase):
    def setUp(self):
        create_file(PYPIRC)
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

    @multipatch
    @patch("danielutils.context_managers.temporary_file.TemporaryFile.read",
           return_value=[f"Found {MypyRunner().bound} errors in 7 files (checked 30 source files)\n"])
    def test_mypy_expect_finish_with_fail_default(self, *args):
        with self.assertRaises(SystemExit):
            publish(
                name=PACAKGE,
                version="0.0.1",
                author="danielnachumdev",
                author_email="danielnachumdev@gmail.com",
                description="A python package to quickly configure and publish a new package",
                homepage="https://github.com/danielnachumdev/quickpub",
                dependencies=["twine", "danielutils"],
                config=AdditionalConfiguration(
                    runners=[
                        MypyRunner()
                    ]
                )
            )

    @multipatch
    @patch("danielutils.context_managers.temporary_file.TemporaryFile.read",
           return_value=[f"Success: no issues found in 1 source file\n"])
    def test_mypy_expect_success(self, *args):
        publish(
            name=PACAKGE,
            version="0.0.1",
            author="danielnachumdev",
            author_email="danielnachumdev@gmail.com",
            description="A python package to quickly configure and publish a new package",
            homepage="https://github.com/danielnachumdev/quickpub",
            dependencies=["twine", "danielutils"],
            config=AdditionalConfiguration(
                runners=[
                    MypyRunner(bound="<=50")
                ]
            )
        )

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
    @patch("danielutils.context_managers.temporary_file.TemporaryFile.read",
           return_value=[f"Found {51} errors in 7 files (checked 30 source files)\n"])
    @patch("builtins.print", _new_print)
    def test_mypy_expect_finished_with_fail_because_failed_bound(self, *args):
        with self.assertRaises(SystemExit):
            publish(
                name=PACAKGE,
                version="0.0.1",
                author="danielnachumdev",
                author_email="danielnachumdev@gmail.com",
                description="A python package to quickly configure and publish a new package",
                homepage="https://github.com/danielnachumdev/quickpub",
                dependencies=["twine", "danielutils"],
                config=AdditionalConfiguration(
                    runners=[
                        MypyRunner(bound="<=50")
                    ]
                )
            )
        self.assertListEqual([('\x1b[38;2;255;0;0mERROR\x1b[0m: ',), ("mypy failed to pass it's defined bound",)],
                             PRINT_QUEUE)
