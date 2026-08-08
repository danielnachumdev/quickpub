import shutil
import unittest
from unittest.mock import MagicMock, patch

from quickpub import UvBuildSchema

from tests.common.base_test_classes import BaseTestClass
from tests.common.helpers import temporary_test_directory

MINIMAL_PYPROJECT = """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "samplepkg"
version = "1.0.0"
requires-python = ">=3.8"
dependencies = []

[tool.setuptools]
packages = ["samplepkg"]
"""


class TestUvBuildSchema(BaseTestClass):
    def test_missing_pyproject_raises(self) -> None:
        with temporary_test_directory() as tmp_dir:
            pyproject_path = tmp_dir / "pyproject.toml"
            with self.assertRaises(UvBuildSchema.EXCEPTION_TYPE):
                UvBuildSchema(str(pyproject_path)).build()

    def test_neither_artifact_raises(self) -> None:
        with self.assertRaises(UvBuildSchema.EXCEPTION_TYPE):
            UvBuildSchema(sdist=False, wheel=False)

    def test_build_command_both_artifacts(self) -> None:
        self.assertEqual(UvBuildSchema().build_command(), "uv build")

    def test_build_command_sdist_only(self) -> None:
        self.assertEqual(
            UvBuildSchema(sdist=True, wheel=False).build_command(),
            "uv build --sdist",
        )

    def test_build_command_wheel_only(self) -> None:
        self.assertEqual(
            UvBuildSchema(sdist=False, wheel=True).build_command(),
            "uv build --wheel",
        )

    @patch(
        "quickpub.strategies.implementations.build_schemas.uv_build_schema.LayeredCommand"
    )
    def test_build_invokes_uv_build(self, mock_layered_command) -> None:
        executor = MagicMock(return_value=(0, "", ""))
        mock_layered_command.return_value.__enter__.return_value = executor

        with temporary_test_directory() as tmp_dir:
            pyproject_path = tmp_dir / "pyproject.toml"
            pyproject_path.write_text(MINIMAL_PYPROJECT, encoding="utf8")
            UvBuildSchema(str(pyproject_path), sdist=True, wheel=False).build()

        executor.assert_called_once_with("uv build --sdist")

    @patch(
        "quickpub.strategies.implementations.build_schemas.uv_build_schema.LayeredCommand"
    )
    def test_build_failure_raises(self, mock_layered_command) -> None:
        executor = MagicMock(return_value=(1, "", "uv failed"))
        mock_layered_command.return_value.__enter__.return_value = executor

        with temporary_test_directory() as tmp_dir:
            pyproject_path = tmp_dir / "pyproject.toml"
            pyproject_path.write_text(MINIMAL_PYPROJECT, encoding="utf8")
            with self.assertRaises(UvBuildSchema.EXCEPTION_TYPE):
                UvBuildSchema(str(pyproject_path)).build()

    @unittest.skipUnless(shutil.which("uv"), "uv is not installed")
    def test_uv_build_creates_sdist(self) -> None:
        with temporary_test_directory() as tmp_dir:
            pyproject_path = tmp_dir / "pyproject.toml"
            pyproject_path.write_text(MINIMAL_PYPROJECT, encoding="utf8")
            package_dir = tmp_dir / "samplepkg"
            package_dir.mkdir()
            (package_dir / "__init__.py").write_text(
                '__version__ = "1.0.0"\n', encoding="utf8"
            )

            UvBuildSchema(str(pyproject_path), sdist=True, wheel=False).build()

            dist_dir = tmp_dir / "dist"
            self.assertTrue(dist_dir.exists())
            tar_files = list(dist_dir.glob("*.tar.gz"))
            self.assertEqual(len(tar_files), 1)
            self.assertIn(tar_files[0].name, {"samplepkg-1.0.0.tar.gz"})
