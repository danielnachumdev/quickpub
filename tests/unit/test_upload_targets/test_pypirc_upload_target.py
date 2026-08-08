import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

from quickpub import ExitEarlyError
from quickpub.strategies.implementations.upload_targets.pypirc_upload_target import (
    PypircUploadTarget,
)

from tests.common.base_test_classes import BaseTestClass
from tests.common.helpers import temporary_test_directory

VALID_PYPIRC = """[distutils]
index-servers =
    pypi
    testpypi

[pypi]
    username = __token__
    password = test_token

[testpypi]
    username = __token__
    password = test_token
"""


def write_pypirc(tmp_dir: Path) -> Path:
    pypirc_path = tmp_dir / ".pypirc"
    pypirc_path.write_text(VALID_PYPIRC, encoding="utf8")
    return pypirc_path


def write_sdist(tmp_dir: Path, filename: str) -> Path:
    dist_dir = tmp_dir / "dist"
    dist_dir.mkdir(exist_ok=True)
    sdist_path = dist_dir / filename
    sdist_path.write_bytes(b"dummy")
    return sdist_path


class TestPypircUploadTarget(BaseTestClass):
    def test_init_default_path(self) -> None:
        target = PypircUploadTarget()
        self.assertEqual(target.pypirc_file_path, "./.pypirc")
        self.assertFalse(target.verbose)

    def test_init_custom_path(self) -> None:
        target = PypircUploadTarget(pypirc_file_path="./custom/.pypirc", verbose=False)
        self.assertEqual(target.pypirc_file_path, "./custom/.pypirc")
        self.assertFalse(target.verbose)

    @patch("quickpub.proxy.cm")
    def test_upload_success(self, mock_cm) -> None:
        mock_cm.return_value = (0, b"success", b"")

        with temporary_test_directory() as tmp_dir:
            pypirc_path = write_pypirc(tmp_dir)
            write_sdist(tmp_dir, "testpackage-1.0.0.tar.gz")

            target = PypircUploadTarget(
                pypirc_file_path=str(pypirc_path), verbose=False
            )
            target.upload(name="testpackage", version="1.0.0")

            mock_cm.assert_called_once_with(
                "twine",
                "upload",
                "--config-file",
                ".pypirc",
                "dist/testpackage-1.0.0.tar.gz",
            )

    @patch("quickpub.proxy.cm")
    def test_upload_uses_normalized_sdist_name(self, mock_cm) -> None:
        mock_cm.return_value = (0, b"success", b"")

        with temporary_test_directory() as tmp_dir:
            pypirc_path = write_pypirc(tmp_dir)
            write_sdist(tmp_dir, "gp-wrapper-1.0.0.tar.gz")

            target = PypircUploadTarget(
                pypirc_file_path=str(pypirc_path), verbose=False
            )
            target.upload(name="gp_wrapper", version="1.0.0")

            mock_cm.assert_called_once_with(
                "twine",
                "upload",
                "--config-file",
                ".pypirc",
                "dist/gp-wrapper-1.0.0.tar.gz",
            )

    def test_upload_missing_sdist(self) -> None:
        with temporary_test_directory() as tmp_dir:
            pypirc_path = write_pypirc(tmp_dir)
            (tmp_dir / "dist").mkdir()

            target = PypircUploadTarget(
                pypirc_file_path=str(pypirc_path), verbose=False
            )
            with self.assertRaises(ExitEarlyError):
                target.upload(name="testpackage", version="1.0.0")

    def test_upload_missing_pypirc_file(self) -> None:
        target = PypircUploadTarget(
            pypirc_file_path="./nonexistent/.pypirc", verbose=False
        )

        with self.assertRaises(RuntimeError) as context:
            target.upload(name="testpackage", version="1.0.0")
        self.assertIn("can't find pypirc file", str(context.exception))

    def test_upload_invalid_pypirc_content(self) -> None:
        invalid_pypirc_content = "invalid content"

        with temporary_test_directory() as tmp_dir:
            pypirc_path = tmp_dir / ".pypirc"
            pypirc_path.write_text(invalid_pypirc_content, encoding="utf8")

            target = PypircUploadTarget(
                pypirc_file_path=str(pypirc_path), verbose=False
            )

            with self.assertRaises(RuntimeError) as context:
                target.upload(name="testpackage", version="1.0.0")
            self.assertIn("failed to match the following regex", str(context.exception))

    @patch("quickpub.proxy.cm")
    def test_upload_failure(self, mock_cm) -> None:
        with temporary_test_directory() as tmp_dir:
            pypirc_path = write_pypirc(tmp_dir)
            write_sdist(tmp_dir, "testpackage-1.0.0.tar.gz")

            mock_cm.return_value = (1, b"", b"upload error")
            target = PypircUploadTarget(
                pypirc_file_path=str(pypirc_path), verbose=False
            )
            with self.assertRaises(ExitEarlyError):
                target.upload(name="testpackage", version="1.0.0")

    @patch("quickpub.proxy.cm")
    @patch(
        "quickpub.strategies.implementations.upload_targets.pypirc_upload_target.logger"
    )
    def test_upload_verbose_mode(self, mock_logger, mock_cm) -> None:
        with temporary_test_directory() as tmp_dir:
            pypirc_path = write_pypirc(tmp_dir)
            write_sdist(tmp_dir, "testpackage-1.0.0.tar.gz")

            mock_cm.return_value = (0, b"success", b"")
            target = PypircUploadTarget(pypirc_file_path=str(pypirc_path), verbose=True)
            target.upload(name="testpackage", version="1.0.0")

            info_calls = [str(call) for call in mock_logger.info.call_args_list]
            info_messages = " ".join(info_calls)
            self.assertIn("Uploading package to PyPI", info_messages)

    def test_validate_file_exists_called(self) -> None:
        valid_pypirc_content = """[distutils]
index-servers =
    pypi
    testpypi

[pypi]
    username = __token__
    password = test_token

[testpypi]
    username = __token__
    password = test_token
"""

        with temporary_test_directory() as tmp_dir:
            pypirc_path = tmp_dir / ".pypirc"
            pypirc_path.write_text(valid_pypirc_content, encoding="utf8")

            target = PypircUploadTarget(
                pypirc_file_path=str(pypirc_path), verbose=False
            )
            target._validate_file_exists()
            self.assertTrue(pypirc_path.exists())

    def test_validate_file_contents_valid(self) -> None:
        valid_pypirc_content = """[distutils]
index-servers =
    pypi
    testpypi

[pypi]
    username = __token__
    password = test_token

[testpypi]
    username = __token__
    password = test_token
"""

        with temporary_test_directory() as tmp_dir:
            pypirc_path = tmp_dir / ".pypirc"
            pypirc_path.write_text(valid_pypirc_content, encoding="utf8")

            target = PypircUploadTarget(
                pypirc_file_path=str(pypirc_path), verbose=False
            )
            target._validate_file_contents()

    def test_validate_file_contents_invalid(self) -> None:
        invalid_pypirc_content = "invalid content"

        with temporary_test_directory() as tmp_dir:
            pypirc_path = tmp_dir / ".pypirc"
            pypirc_path.write_text(invalid_pypirc_content, encoding="utf8")

            target = PypircUploadTarget(
                pypirc_file_path=str(pypirc_path), verbose=False
            )

            with self.assertRaises(RuntimeError) as context:
                target._validate_file_contents()
            self.assertIn("failed to match the following regex", str(context.exception))


if __name__ == "__main__":
    unittest.main()
