from quickpub import PypircEnforcer

from tests.base_test_classes import BaseTestClass
from tests.test_helpers import temporary_test_directory

TMP_PYPIRC_PATH: str = ".TMP_PYPIRC"


class TestPypircEnforcer(BaseTestClass):
    def test_no_file_should_fail(self) -> None:
        with temporary_test_directory() as tmp_dir:
            pypirc_path = tmp_dir / TMP_PYPIRC_PATH
            with self.assertRaises(PypircEnforcer.EXCEPTION_TYPE):
                PypircEnforcer(str(pypirc_path)).enforce()

            with self.assertRaises(PypircEnforcer.EXCEPTION_TYPE):
                PypircEnforcer(str(pypirc_path), False).enforce()

    def test_file_exists_no_check_format_should_pass(self) -> None:
        with temporary_test_directory() as tmp_dir:
            pypirc_path = tmp_dir / TMP_PYPIRC_PATH
            pypirc_path.write_text("asjbdalkjgn;asljkgn agn a;ljsgn weg na;kjb")
            PypircEnforcer(str(pypirc_path), False).enforce()

    def test_file_exists_and_check_format_should_fail(self) -> None:
        with temporary_test_directory() as tmp_dir:
            pypirc_path = tmp_dir / TMP_PYPIRC_PATH
            pypirc_path.write_text("asjbdalkjgn;asljkgn agn a;ljsgn weg na;kjb")
            with self.assertRaises(PypircEnforcer.EXCEPTION_TYPE):
                PypircEnforcer(str(pypirc_path)).enforce()

    def test_file_exists_and_check_format_should_pass(self) -> None:
        with temporary_test_directory() as tmp_dir:
            pypirc_path = tmp_dir / TMP_PYPIRC_PATH
            pypirc_path.write_text(
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
            PypircEnforcer(str(pypirc_path)).enforce()
