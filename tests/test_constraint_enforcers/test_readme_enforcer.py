import unittest

from danielutils import create_file, delete_file

from quickpub import ReadmeEnforcer
from utils import AutoCWDTestCase

TMP_README_PATH: str = "./TMP_README.md"


class TestReadmeEnforcer(AutoCWDTestCase):
    def test_readme_exists_should_not_fail(self) -> None:
        create_file(TMP_README_PATH)
        ReadmeEnforcer(TMP_README_PATH).enforce()

    def test_readme_doesnt_exists_should_fail(self) -> None:
        with self.assertRaises(ReadmeEnforcer.EXCEPTION_TYPE):
            ReadmeEnforcer(TMP_README_PATH).enforce()
