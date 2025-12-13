import unittest
from unittest.mock import patch

from quickpub import ExitEarlyError, Version, Dependency
from quickpub.validators import (
    validate_version,
    validate_python_version,
    validate_keywords,
    validate_dependencies,
    validate_source,
)

from tests.base_test_classes import BaseTestClass


class TestValidateVersion(BaseTestClass):
    def test_none_version_raises_error(self) -> None:
        with self.assertRaises(ExitEarlyError) as context:
            validate_version(None)
        self.assertIn("Must supply a version number", str(context.exception))

    def test_empty_string_version_raises_error(self) -> None:
        with self.assertRaises(ExitEarlyError) as context:
            validate_version("")
        self.assertIn("Must supply a version number", str(context.exception))

    def test_valid_version_object_returns_same(self) -> None:
        version = Version(1, 2, 3)
        result = validate_version(version)
        self.assertEqual(result, version)
        self.assertIs(result, version)

    def test_valid_version_string_returns_version_object(self) -> None:
        result = validate_version("1.2.3")
        self.assertIsInstance(result, Version)
        self.assertEqual(result.major, 1)
        self.assertEqual(result.minor, 2)
        self.assertEqual(result.patch, 3)

    def test_invalid_type_raises_error(self) -> None:
        with self.assertRaises(ExitEarlyError) as context:
            validate_version(123)
        self.assertIn(
            "Version must be a string or Version object", str(context.exception)
        )

    def test_invalid_string_format_raises_error(self) -> None:
        with self.assertRaises(ExitEarlyError):
            validate_version("invalid.version.format.here")


class TestValidatePythonVersion(BaseTestClass):
    @patch("quickpub.validators.get_python_version")
    def test_none_uses_current_python_version(self, mock_get_version) -> None:
        mock_get_version.return_value = (3, 10, 11)
        result = validate_python_version(None)
        self.assertIsInstance(result, Version)
        self.assertEqual(result.major, 3)
        self.assertEqual(result.minor, 10)
        self.assertEqual(result.patch, 11)
        mock_get_version.assert_called_once()

    def test_provided_version_returns_same(self) -> None:
        version = Version(3, 9, 0)
        result = validate_python_version(version)
        self.assertEqual(result, version)
        self.assertIs(result, version)


class TestValidateKeywords(BaseTestClass):
    def test_none_returns_empty_list(self) -> None:
        result = validate_keywords(None)
        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    def test_empty_list_returns_empty_list(self) -> None:
        result = validate_keywords([])
        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    def test_valid_list_returns_same(self) -> None:
        keywords = ["test", "package", "publishing"]
        result = validate_keywords(keywords)
        self.assertEqual(result, keywords)
        self.assertIs(result, keywords)


class TestValidateDependencies(BaseTestClass):
    def test_none_returns_empty_list(self) -> None:
        result = validate_dependencies(None)
        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    def test_empty_list_returns_empty_list(self) -> None:
        result = validate_dependencies([])
        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    def test_string_dependencies_converted(self) -> None:
        deps = ["package1>=1.0.0", "package2==2.0.0"]
        result = validate_dependencies(deps)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Dependency)
        self.assertIsInstance(result[1], Dependency)
        self.assertEqual(result[0].name, "package1")
        self.assertEqual(result[1].name, "package2")

    def test_dependency_objects_preserved(self) -> None:
        dep1 = Dependency("package1", ">=", Version(1, 0, 0))
        dep2 = Dependency("package2", "==", Version(2, 0, 0))
        deps = [dep1, dep2]
        result = validate_dependencies(deps)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], dep1)
        self.assertEqual(result[1], dep2)

    def test_mixed_string_and_dependency_objects(self) -> None:
        dep1 = Dependency("package1", ">=", Version(1, 0, 0))
        deps = [dep1, "package2==2.0.0"]
        result = validate_dependencies(deps)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Dependency)
        self.assertIsInstance(result[1], Dependency)
        self.assertEqual(result[0], dep1)
        self.assertEqual(result[1].name, "package2")


class TestValidateSource(BaseTestClass):
    def test_none_uses_default_path(self) -> None:
        package_name = "testpackage"
        result = validate_source(package_name, None)
        expected = f"./{package_name}"
        self.assertEqual(result, expected)

    def test_provided_path_returns_same(self) -> None:
        package_name = "testpackage"
        custom_path = "./custom/path"
        result = validate_source(package_name, custom_path)
        self.assertEqual(result, custom_path)

    def test_provided_path_with_different_name(self) -> None:
        package_name = "testpackage"
        custom_path = "./different_name"
        result = validate_source(package_name, custom_path)
        self.assertEqual(result, custom_path)


if __name__ == "__main__":
    unittest.main()
