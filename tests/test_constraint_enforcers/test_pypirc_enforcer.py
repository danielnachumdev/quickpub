import unittest

from danielutils import create_file, delete_file

from quickpub import PypircEnforcer

TMP_PYPIRC_PATH: str = "./.TMP_PYPIRC"


class TestPypircEnforcer(unittest.TestCase):
    def test_no_file_should_fail(self) -> None:
        with self.assertRaises(PypircEnforcer.EXCEPTION_TYPE):
            PypircEnforcer(TMP_PYPIRC_PATH).enforce()

        with self.assertRaises(PypircEnforcer.EXCEPTION_TYPE):
            PypircEnforcer(TMP_PYPIRC_PATH, False).enforce()

    def test_file_exists_no_check_format_should_pass(self) -> None:
        exp = None
        with open(TMP_PYPIRC_PATH, "w") as f:
            f.write("asjbdalkjgn;asljkgn agn a;ljsgn weg na;kjb")
        try:
            PypircEnforcer(TMP_PYPIRC_PATH, False).enforce()
        except Exception as e:
            exp = e
        delete_file(TMP_PYPIRC_PATH)
        if exp:
            raise exp

    def test_file_exists_and_check_format_should_fail(self) -> None:
        with open(TMP_PYPIRC_PATH, "w") as f:
            f.write("asjbdalkjgn;asljkgn agn a;ljsgn weg na;kjb")
        try:
            with self.assertRaises(PypircEnforcer.EXCEPTION_TYPE):
                PypircEnforcer(TMP_PYPIRC_PATH).enforce()
        finally:
            delete_file(TMP_PYPIRC_PATH)

    def test_file_exists_and_check_format_should_pass(self) -> None:
        with open(TMP_PYPIRC_PATH, "w") as f:
            f.write("""[distutils]
index-servers =
    pypi
    testpypi

[pypi]
    username = __token__
    password = aaaaaaaaaaaaaaaaa

[testpypi]
    username = __token__
    password = aaaaaaaaaaaaaaaaa
""")
        try:
            PypircEnforcer(TMP_PYPIRC_PATH).enforce()
        finally:
            delete_file(TMP_PYPIRC_PATH)