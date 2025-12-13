from quickpub import SetuptoolsBuildSchema

from tests.base_test_classes import BaseTestClass
from tests.test_helpers import temporary_test_directory

TMP_SETUP_FILE_PATH: str = "tmp_setup.py"
TMP_TOML_FILE_PATH: str = "tmp_pyproject.toml"
EXPECTED_CONTENTS = """from setuptools import setup

setup()
"""


class TestSetupToolsBuildSchema(BaseTestClass):
    def test_no_setup_file(self) -> None:
        with temporary_test_directory() as tmp_dir:
            setup_path = tmp_dir / TMP_SETUP_FILE_PATH
            with self.assertRaises(SetuptoolsBuildSchema.EXCEPTION_TYPE):
                SetuptoolsBuildSchema(str(setup_path)).build()

    def test_no_toml(self) -> None:
        with temporary_test_directory() as tmp_dir:
            setup_path = tmp_dir / TMP_SETUP_FILE_PATH
            setup_path.write_text(EXPECTED_CONTENTS)
            SetuptoolsBuildSchema(str(setup_path), "toml").build()
            subdirs = [d.name for d in tmp_dir.iterdir() if d.is_dir()]
            self.assertEqual(2, len(subdirs), "Expected only 2 subdirectories")
            self.assertTrue(subdirs[0] == "dist", "dist folder does not exist")
            self.assertTrue(
                subdirs[1].endswith(".egg-info"),
                "folder that ends with '.egg-info' does not exist ",
            )

    def test_toml_backend(self) -> None:
        with temporary_test_directory() as tmp_dir:
            setup_path = tmp_dir / TMP_SETUP_FILE_PATH
            toml_path = tmp_dir / TMP_TOML_FILE_PATH
            setup_path.write_text(EXPECTED_CONTENTS)
            toml_path.touch()
            SetuptoolsBuildSchema(str(setup_path), "toml").build()
