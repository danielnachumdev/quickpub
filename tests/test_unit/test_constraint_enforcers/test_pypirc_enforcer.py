from danielutils import AutoCWDTestCase
from quickpub import PypircEnforcer

TMP_PYPIRC_PATH: str = "./.TMP_PYPIRC"


class TestPypircEnforcer(AutoCWDTestCase):
    def test_no_file_should_fail(self) -> None:
        with self.assertRaises(PypircEnforcer.EXCEPTION_TYPE):
            PypircEnforcer(TMP_PYPIRC_PATH).enforce()

        with self.assertRaises(PypircEnforcer.EXCEPTION_TYPE):
            PypircEnforcer(TMP_PYPIRC_PATH, False).enforce()

    def test_file_exists_no_check_format_should_pass(self) -> None:
        with open(TMP_PYPIRC_PATH, "w") as f:
            f.write("asjbdalkjgn;asljkgn agn a;ljsgn weg na;kjb")
        PypircEnforcer(TMP_PYPIRC_PATH, False).enforce()

    def test_file_exists_and_check_format_should_fail(self) -> None:
        with open(TMP_PYPIRC_PATH, "w") as f:
            f.write("asjbdalkjgn;asljkgn agn a;ljsgn weg na;kjb")
        with self.assertRaises(PypircEnforcer.EXCEPTION_TYPE):
            PypircEnforcer(TMP_PYPIRC_PATH).enforce()

    def test_file_exists_and_check_format_should_pass(self) -> None:
        with open(TMP_PYPIRC_PATH, "w") as f:
            f.write(
                """[distutils]
index-servers =
    pypi
    testpypi

[pypi]
    username = __token__
    password = aaaaaaaaaaaaaaaaa

[testpypi]
    username = __token__
    password = aaaaaaaaaaaaaaaaa
"""
            )
        PypircEnforcer(TMP_PYPIRC_PATH).enforce()
