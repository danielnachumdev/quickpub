import unittest

from danielutils import create_file, delete_file

from quickpub import ReadmeEnforcer

TMP_README_PATH: str = "./TMP_README.md"


class TestReadmeEnforcer(unittest.TestCase):
    def test_readme_exists_should_not_fail(self) -> None:
        exp = None
        create_file(TMP_README_PATH)
        try:
            ReadmeEnforcer(TMP_README_PATH).enforce()
        except Exception as e:
            exp = e
        delete_file(TMP_README_PATH)
        if exp:
            raise exp

    def test_readme_doesnt_exists_should_fail(self) -> None:
        with self.assertRaises(ReadmeEnforcer.EXCEPTION_TYPE):
            ReadmeEnforcer(TMP_README_PATH).enforce()
