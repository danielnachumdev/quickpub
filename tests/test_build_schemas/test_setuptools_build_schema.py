from danielutils import get_current_working_directory, create_file, get_directories, AutoCWDTestCase
from quickpub import SetuptoolsBuildSchema

TMP_SETUP_FILE_PATH: str = "./tmp_setup.py"
TMP_TOML_FILE_PATH: str = "./tmp_pyproject.toml"
EXPECTED_CONTENTS = """from setuptools import setup

setup()
"""


class TestSetupToolsBuildSchema(AutoCWDTestCase):
    def test_no_setup_file(self) -> None:
        with self.assertRaises(SetuptoolsBuildSchema.EXCEPTION_TYPE):
            SetuptoolsBuildSchema(TMP_SETUP_FILE_PATH).build()

    def test_no_toml(self) -> None:
        with open(TMP_SETUP_FILE_PATH, "w") as f:
            f.write(EXPECTED_CONTENTS)
        SetuptoolsBuildSchema(TMP_SETUP_FILE_PATH, "toml").build()
        subdirs = get_directories(get_current_working_directory())
        self.assertEqual(2, len(subdirs), "Expected only 2 subdirectories")
        self.assertTrue(subdirs[0] == "dist", "dist folder does not exist")
        self.assertTrue(subdirs[1].endswith(".egg-info"), "folder that ends with '.egg-info' does not exist ")

    def test_toml_backend(self) -> None:
        with open(TMP_SETUP_FILE_PATH, "w") as f:
            f.write(EXPECTED_CONTENTS)
        create_file(TMP_TOML_FILE_PATH)
        SetuptoolsBuildSchema(TMP_SETUP_FILE_PATH, "toml").build()
