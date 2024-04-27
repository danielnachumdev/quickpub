import unittest
from unittest.mock import Mock, patch, MagicMock
from quickpub import publish
from danielutils import create_file, delete_file, create_directory, delete_directory
from requests import Response

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


from danielutils import chain_decorators

mock_response = Response()
multipatch = chain_decorators(
    patch("quickpub.proxy.get", return_value=mock_response),
    patch("quickpub.proxy.cm", return_value=(0, b"", b"")),
)


class TestMain(unittest.TestCase):

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

    @patch("quickpub.proxy.cm", return_value=(0, b"", b""))
    def test_main_no_pypirc(self, mock_func):
        delete_file(PYPIRC)
        with self.assertRaises(SystemExit) as se:
            f()
        self.assertEqual(se.exception.code, 1)

    @patch("quickpub.proxy.cm", return_value=(0, b"", b""))
    def test_main_no_readme(self, *args: MagicMock):
        delete_file(README)
        with self.assertRaises(SystemExit) as se:
            f()
        self.assertEqual(se.exception.code, 1)

    @patch("quickpub.proxy.cm", return_value=(0, b"", b""))
    def test_main_no_license(self, *args: MagicMock):
        delete_file(LICENSE)
        with self.assertRaises(SystemExit) as se:
            f()
        self.assertEqual(se.exception.code, 1)

    @patch("quickpub.proxy.cm", return_value=(0, b"", b""))
    def test_main_wrong_version(self, *args: MagicMock):
        create_directory("dist")
        create_file(f"dist/{PACAKGE}-0.0.1.tar.gz")
        with self.assertRaises(SystemExit) as se:
            f()
        self.assertEqual(se.exception.code, 1)
