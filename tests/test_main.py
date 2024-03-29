import unittest
from unittest.mock import Mock, patch
from quickpub import publish
import quickpub
from danielutils import create_file, delete_file, create_directory, delete_directory

PYPIRC = "./.pypirc"
PACAKGE = "pacakge"
README = "./README.md"
LICENSE = "./LICENSE"


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
        delete_directory("dist")
        delete_directory(f"{PACAKGE}.egg-info")
        delete_file("setup.py")
        delete_file("pyproject.toml")

    @patch("quickpub.proxy.cm", return_value=(0, b"", b""))
    def test_main_simple_should_pass(self, mock_func):
        f()

    @patch("quickpub.proxy.cm", return_value=(0, b"", b""))
    def test_main_no_pypirc(self, mock_func):
        delete_file(PYPIRC)
        with self.assertRaises(SystemExit) as se:
            f()
        self.assertEqual(se.exception.code, 1)

    @patch("quickpub.proxy.cm", return_value=(0, b"", b""))
    def test_main_no_readme(self, mock_func):
        delete_file(README)
        with self.assertRaises(SystemExit) as se:
            f()
        self.assertEqual(se.exception.code, 1)

    @patch("quickpub.proxy.cm", return_value=(0, b"", b""))
    def test_main_no_license(self, mock_func):
        delete_file(LICENSE)
        with self.assertRaises(SystemExit) as se:
            f()
        self.assertEqual(se.exception.code, 1)

    @patch("quickpub.proxy.cm", return_value=(0, b"", b""))
    def test_main_wrong_version(self, mock_func):
        v = "0.0.1"
        create_directory("dist")
        create_file(f"dist/{PACAKGE}-{v}.tar.gz")
        with self.assertRaises(SystemExit) as se:
            publish(
                name=PACAKGE,
                version=v,
                author="danielnachumdev",
                author_email="danielnachumdev@gmail.com",
                description="A python package to quickly configure and publish a new package",
                homepage="https://github.com/danielnachumdev/quickpub",
                dependencies=["twine", "danielutils"]
            )
        self.assertEqual(se.exception.code, 1)

