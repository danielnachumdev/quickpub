from quickpub import ReadmeEnforcer

from tests.base_test_classes import BaseTestClass
from tests.test_helpers import temporary_test_directory

TMP_README_PATH: str = "TMP_README.md"


class TestReadmeEnforcer(BaseTestClass):
    def test_readme_exists_should_not_fail(self) -> None:
        with temporary_test_directory() as tmp_dir:
            readme_path = tmp_dir / TMP_README_PATH
            readme_path.touch()
            ReadmeEnforcer(str(readme_path)).enforce()

    def test_readme_doesnt_exists_should_fail(self) -> None:
        with temporary_test_directory() as tmp_dir:
            readme_path = tmp_dir / TMP_README_PATH
            with self.assertRaises(ReadmeEnforcer.EXCEPTION_TYPE):
                ReadmeEnforcer(str(readme_path)).enforce()
