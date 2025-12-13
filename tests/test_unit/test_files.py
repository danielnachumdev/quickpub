import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from quickpub import Version, Dependency
from quickpub.classifiers import (
    DevelopmentStatusClassifier,
    IntendedAudienceClassifier,
    ProgrammingLanguageClassifier,
    OperatingSystemClassifier,
)
from quickpub.files import (
    create_toml,
    create_setup,
    create_manifest,
    add_version_to_init,
    _format_classifiers_string,
    _build_py_typed_section,
    _build_scripts_section,
    _build_toml_content,
)

from tests.base_test_classes import BaseTestClass
from tests.test_helpers import temporary_test_directory


class TestFormatClassifiersString(BaseTestClass):
    def test_empty_list_returns_empty_string(self) -> None:
        result = _format_classifiers_string([])
        self.assertEqual(result, "")

    def test_single_classifier(self) -> None:
        from quickpub.classifiers import Classifier

        classifiers: list[Classifier] = [
            DevelopmentStatusClassifier.Alpha
        ]  # type: ignore[list-item]
        result = _format_classifiers_string(classifiers)
        self.assertIn('"Development Status :: 3 - Alpha"', result)
        self.assertTrue(result.startswith("\n\t"))
        self.assertTrue(result.endswith("\n"))

    def test_multiple_classifiers(self) -> None:
        classifiers = [
            DevelopmentStatusClassifier.Alpha,
            IntendedAudienceClassifier.Developers,
            ProgrammingLanguageClassifier.Python3,
        ]
        result = _format_classifiers_string(classifiers)
        self.assertIn('"Development Status :: 3 - Alpha"', result)
        self.assertIn('"Intended Audience :: Developers"', result)
        self.assertIn('"Programming Language :: Python :: 3"', result)
        self.assertTrue(result.startswith("\n\t"))
        self.assertTrue(result.endswith("\n"))


class TestBuildPyTypedSection(BaseTestClass):
    @patch("quickpub.files.get_files")
    def test_with_py_typed_file(self, mock_get_files) -> None:
        mock_get_files.return_value = ["file1.py", "py.typed", "file2.py"]
        result = _build_py_typed_section("testpackage", "./testpackage")
        self.assertIn("[tool.setuptools.package-data]", result)
        self.assertIn('"testpackage" = ["py.typed"]', result)
        mock_get_files.assert_called_once_with("./testpackage")

    @patch("quickpub.files.get_files")
    def test_without_py_typed_file(self, mock_get_files) -> None:
        mock_get_files.return_value = ["file1.py", "file2.py"]
        result = _build_py_typed_section("testpackage", "./testpackage")
        self.assertEqual(result, "")
        mock_get_files.assert_called_once_with("./testpackage")

    @patch("quickpub.files.get_files")
    def test_empty_files_list(self, mock_get_files) -> None:
        mock_get_files.return_value = []
        result = _build_py_typed_section("testpackage", "./testpackage")
        self.assertEqual(result, "")


class TestBuildScriptsSection(BaseTestClass):
    def test_empty_dict_returns_section_header(self) -> None:
        result = _build_scripts_section("testpackage", {})
        self.assertIn("[project.scripts]", result)
        self.assertTrue(result.endswith("\n"))

    def test_single_script(self) -> None:
        def my_function() -> None:
            pass

        my_function.__module__ = "mymodule"
        my_function.__name__ = "my_function"

        scripts = {"myscript": my_function}
        result = _build_scripts_section("testpackage", scripts)
        self.assertIn("[project.scripts]", result)
        self.assertIn('myscript = "mymodule:my_function"', result)

    def test_multiple_scripts(self) -> None:
        def func1() -> None:
            pass

        def func2() -> None:
            pass

        func1.__module__ = "module1"
        func1.__name__ = "func1"
        func2.__module__ = "module2"
        func2.__name__ = "func2"

        scripts = {"script1": func1, "script2": func2}
        result = _build_scripts_section("testpackage", scripts)
        self.assertIn("[project.scripts]", result)
        self.assertIn('script1 = "module1:func1"', result)
        self.assertIn('script2 = "module2:func2"', result)

    def test_main_module_handling(self) -> None:
        def main_func() -> None:
            pass

        main_func.__module__ = "__main__"
        main_func.__name__ = "main_func"

        scripts = {"main": main_func}
        result = _build_scripts_section("testpackage", scripts)
        self.assertIn("[project.scripts]", result)
        self.assertIn('main = "testpackage.__main__:main_func"', result)


class TestBuildTomlContent(BaseTestClass):
    def test_full_toml_content(self) -> None:
        name = "testpackage"
        version = Version(1, 2, 3)
        author = "Test Author"
        author_email = "test@example.com"
        description = "Test description"
        readme_file_path = "./README.md"
        license_file_path = "./LICENSE"
        keywords = ["test", "package"]
        min_python = Version(3, 8, 0)
        dependencies = [Dependency("dep1", ">=", Version(1, 0, 0))]
        classifiers_string = '\n\t"Classifier1"\n'
        scripts_section = '\n[project.scripts]\n    script = "module:func"\n'
        py_typed = '[tool.setuptools.package-data]\n"testpackage" = ["py.typed"]'
        homepage = "https://example.com"

        result = _build_toml_content(
            name,
            version,
            author,
            author_email,
            description,
            readme_file_path,
            license_file_path,
            keywords,
            min_python,
            dependencies,
            classifiers_string,
            scripts_section,
            py_typed,
            homepage,
        )

        self.assertIn("[build-system]", result)
        self.assertIn('name = "testpackage"', result)
        self.assertIn('version = "1.2.3"', result)
        self.assertIn('name = "Test Author"', result)
        self.assertIn('email = "test@example.com"', result)
        self.assertIn('description = "Test description"', result)
        self.assertIn('readme = {file = "./README.md"', result)
        self.assertIn('license = { "file" = "./LICENSE" }', result)
        self.assertIn("keywords = ['test', 'package']", result)
        self.assertIn('requires-python = ">=3.8.0"', result)
        self.assertIn("Classifier1", result)
        self.assertIn("[project.scripts]", result)
        self.assertIn('packages = ["testpackage"]', result)
        self.assertIn('"Homepage" = "https://example.com"', result)
        self.assertIn('"Bug Tracker" = "https://example.com/issues"', result)


class TestCreateToml(BaseTestClass):
    @patch("quickpub.files.get_files")
    def test_create_toml_basic(self, mock_get_files) -> None:
        mock_get_files.return_value = []
        with temporary_test_directory() as tmp_dir:
            package_dir = tmp_dir / "testpackage"
            package_dir.mkdir()
            readme_file = tmp_dir / "README.md"
            readme_file.write_text("# Test Package\n", encoding="utf8")
            license_file = tmp_dir / "LICENSE"
            license_file.write_text("MIT License\n", encoding="utf8")

            create_toml(
                name="testpackage",
                src_folder_path=str(package_dir),
                readme_file_path=str(readme_file),
                license_file_path=str(license_file),
                version=Version(1, 0, 0),
                author="Test Author",
                author_email="test@example.com",
                description="Test description",
                homepage="https://example.com",
                keywords=["test"],
                min_python=Version(3, 8, 0),
                dependencies=[],
                classifiers=[DevelopmentStatusClassifier.Alpha],
            )

            toml_file = tmp_dir / "pyproject.toml"
            self.assertTrue(toml_file.exists())
            content = toml_file.read_text(encoding="utf8")
            self.assertIn('name = "testpackage"', content)
            self.assertIn('version = "1.0.0"', content)

    @patch("quickpub.files.get_files")
    def test_create_toml_with_py_typed(self, mock_get_files) -> None:
        mock_get_files.return_value = ["py.typed"]
        with temporary_test_directory() as tmp_dir:
            package_dir = tmp_dir / "testpackage"
            package_dir.mkdir()
            readme_file = tmp_dir / "README.md"
            readme_file.write_text("# Test Package\n", encoding="utf8")
            license_file = tmp_dir / "LICENSE"
            license_file.write_text("MIT License\n", encoding="utf8")

            create_toml(
                name="testpackage",
                src_folder_path=str(package_dir),
                readme_file_path=str(readme_file),
                license_file_path=str(license_file),
                version=Version(1, 0, 0),
                author="Test Author",
                author_email="test@example.com",
                description="Test description",
                homepage="https://example.com",
                keywords=[],
                min_python=Version(3, 8, 0),
                dependencies=[],
                classifiers=[],
            )

            toml_file = tmp_dir / "pyproject.toml"
            content = toml_file.read_text(encoding="utf8")
            self.assertIn("[tool.setuptools.package-data]", content)
            self.assertIn('"testpackage" = ["py.typed"]', content)

    @patch("quickpub.files.get_files")
    def test_create_toml_with_scripts(self, mock_get_files) -> None:
        mock_get_files.return_value = []

        def my_script() -> None:
            pass

        my_script.__module__ = "mymodule"
        my_script.__name__ = "my_script"

        with temporary_test_directory() as tmp_dir:
            package_dir = tmp_dir / "testpackage"
            package_dir.mkdir()
            readme_file = tmp_dir / "README.md"
            readme_file.write_text("# Test Package\n", encoding="utf8")
            license_file = tmp_dir / "LICENSE"
            license_file.write_text("MIT License\n", encoding="utf8")

            create_toml(
                name="testpackage",
                src_folder_path=str(package_dir),
                readme_file_path=str(readme_file),
                license_file_path=str(license_file),
                version=Version(1, 0, 0),
                author="Test Author",
                author_email="test@example.com",
                description="Test description",
                homepage="https://example.com",
                keywords=[],
                min_python=Version(3, 8, 0),
                dependencies=[],
                classifiers=[],
                scripts={"myscript": my_script},
            )

            toml_file = tmp_dir / "pyproject.toml"
            content = toml_file.read_text(encoding="utf8")
            self.assertIn("[project.scripts]", content)
            self.assertIn('myscript = "mymodule:my_script"', content)

    @patch("quickpub.files.get_files")
    def test_create_toml_with_dependencies(self, mock_get_files) -> None:
        mock_get_files.return_value = []
        deps = [
            Dependency("dep1", ">=", Version(1, 0, 0)),
            Dependency("dep2", "==", Version(2, 0, 0)),
        ]

        with temporary_test_directory() as tmp_dir:
            package_dir = tmp_dir / "testpackage"
            package_dir.mkdir()
            readme_file = tmp_dir / "README.md"
            readme_file.write_text("# Test Package\n", encoding="utf8")
            license_file = tmp_dir / "LICENSE"
            license_file.write_text("MIT License\n", encoding="utf8")

            create_toml(
                name="testpackage",
                src_folder_path=str(package_dir),
                readme_file_path=str(readme_file),
                license_file_path=str(license_file),
                version=Version(1, 0, 0),
                author="Test Author",
                author_email="test@example.com",
                description="Test description",
                homepage="https://example.com",
                keywords=[],
                min_python=Version(3, 8, 0),
                dependencies=deps,
                classifiers=[],
            )

            toml_file = tmp_dir / "pyproject.toml"
            content = toml_file.read_text(encoding="utf8")
            self.assertIn("dep1>=1.0.0", content)
            self.assertIn("dep2==2.0.0", content)


class TestCreateSetup(BaseTestClass):
    def test_create_setup(self) -> None:
        with temporary_test_directory() as tmp_dir:
            create_setup()

            setup_file = tmp_dir / "setup.py"
            self.assertTrue(setup_file.exists())
            content = setup_file.read_text(encoding="utf8")
            self.assertEqual(content, "from setuptools import setup\n\nsetup()\n")


class TestCreateManifest(BaseTestClass):
    def test_create_manifest(self) -> None:
        with temporary_test_directory() as tmp_dir:
            create_manifest(name="testpackage")

            manifest_file = tmp_dir / "MANIFEST.in"
            self.assertTrue(manifest_file.exists())
            content = manifest_file.read_text(encoding="utf8")
            self.assertEqual(content, "recursive-include testpackage *.py")

    def test_create_manifest_different_name(self) -> None:
        with temporary_test_directory() as tmp_dir:
            create_manifest(name="mypackage")

            manifest_file = tmp_dir / "MANIFEST.in"
            content = manifest_file.read_text(encoding="utf8")
            self.assertEqual(content, "recursive-include mypackage *.py")


class TestAddVersionToInit(BaseTestClass):
    def test_adds_version_to_init_when_missing(self) -> None:
        with temporary_test_directory() as tmp_dir:
            package_dir = tmp_dir / "testpackage"
            package_dir.mkdir()
            init_file = package_dir / "__init__.py"
            init_file.write_text(
                "from .structures import *\nfrom .strategies import *\n",
                encoding="utf8",
            )

            add_version_to_init(
                src_folder_path=str(package_dir),
                version=Version(1, 2, 3),
            )

            content = init_file.read_text(encoding="utf8")
            self.assertIn('__version__ = "1.2.3"', content)
            self.assertIn("from .structures import *", content)
            self.assertIn("from .strategies import *", content)

    def test_updates_existing_version(self) -> None:
        with temporary_test_directory() as tmp_dir:
            package_dir = tmp_dir / "testpackage"
            package_dir.mkdir()
            init_file = package_dir / "__init__.py"
            init_file.write_text(
                '__version__ = "1.0.0"\nfrom .structures import *\n', encoding="utf8"
            )

            add_version_to_init(
                src_folder_path=str(package_dir),
                version=Version(2, 0, 0),
            )

            content = init_file.read_text(encoding="utf8")
            self.assertIn('__version__ = "2.0.0"', content)
            self.assertNotIn('__version__ = "1.0.0"', content)
            self.assertIn("from .structures import *", content)

    def test_preserves_file_structure(self) -> None:
        with temporary_test_directory() as tmp_dir:
            package_dir = tmp_dir / "testpackage"
            package_dir.mkdir()
            original_content = """from .structures import *
from .strategies import *
from .enforcers import ExitEarlyError
from .qa import SupportsProgress
from .logging_ import set_log_level
from .__main__ import publish, main
"""
            init_file = package_dir / "__init__.py"
            init_file.write_text(original_content, encoding="utf8")

            add_version_to_init(
                src_folder_path=str(package_dir),
                version=Version(3, 1, 0),
            )

            content = init_file.read_text(encoding="utf8")
            self.assertIn('__version__ = "3.1.0"', content)
            for line in original_content.strip().split("\n"):
                if line.strip():
                    self.assertIn(line.strip(), content)

    def test_creates_init_file_when_missing(self) -> None:
        with temporary_test_directory() as tmp_dir:
            package_dir = tmp_dir / "testpackage"
            package_dir.mkdir()
            init_file = package_dir / "__init__.py"

            self.assertFalse(init_file.exists())
            add_version_to_init(
                src_folder_path=str(package_dir),
                version=Version(1, 0, 0),
            )

            self.assertTrue(init_file.exists())
            content = init_file.read_text(encoding="utf8")
            self.assertIn('__version__ = "1.0.0"', content)

    def test_handles_empty_init_file(self) -> None:
        with temporary_test_directory() as tmp_dir:
            package_dir = tmp_dir / "testpackage"
            package_dir.mkdir()
            init_file = package_dir / "__init__.py"
            init_file.write_text("", encoding="utf8")

            add_version_to_init(
                src_folder_path=str(package_dir),
                version=Version(1, 0, 0),
            )

            content = init_file.read_text(encoding="utf8")
            self.assertIn('__version__ = "1.0.0"', content)


if __name__ == "__main__":
    unittest.main()
