import unittest
from unittest.mock import Mock, patch, MagicMock
from danielutils import create_file, delete_file, create_directory, delete_directory, chain_decorators
import requests

from quickpub import publish

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


class TestMissingFiles(unittest.TestCase):

    def setUp(self):
        create_file(PYPIRC)
        create_directory(PACAKGE)
        create_file(README)
        create_file(LICENSE)

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
    def test_main_simple_should_pass(self, *args: MagicMock):
        f()

    @multipatch
    def test_main_no_pypirc(self, *args):
        delete_file(PYPIRC)
        with self.assertRaises(SystemExit) as se:
            f()
        self.assertEqual(se.exception.code, 1)

    @multipatch
    def test_main_no_readme(self, *args: MagicMock):
        delete_file(README)
        with self.assertRaises(SystemExit) as se:
            f()
        self.assertEqual(se.exception.code, 1)

    @multipatch
    def test_main_no_license(self, *args: MagicMock):
        delete_file(LICENSE)
        with self.assertRaises(SystemExit) as se:
            f()
        self.assertEqual(se.exception.code, 1)

    @multipatch
    def test_main_wrong_version(self, *args: MagicMock):
        create_directory("dist")
        create_file(f"dist/{PACAKGE}-0.0.1.tar.gz")
        with self.assertRaises(SystemExit) as se:
            f()
        self.assertEqual(se.exception.code, 1)
