import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

import fire

from quickpub import ExitEarlyError, Version, Dependency
from quickpub.__main__ import (
    _validate_publish_inputs,
    _run_constraint_enforcers,
    _run_quality_assurance,
    _create_package_files,
    _build_and_upload_packages,
    publish,
    main,
)

from tests.base_test_classes import BaseTestClass
from tests.test_helpers import temporary_test_directory


class TestValidatePublishInputs(BaseTestClass):
    @patch("quickpub.__main__.validate_dependencies")
    @patch("quickpub.__main__.validate_keywords")
    @patch("quickpub.__main__.validate_python_version")
    @patch("quickpub.__main__.validate_source")
    @patch("quickpub.__main__.validate_version")
    def test_all_validations_called(
        self,
        mock_validate_version,
        mock_validate_source,
        mock_validate_python_version,
        mock_validate_keywords,
        mock_validate_dependencies,
    ) -> None:
        mock_validate_version.return_value = Version(1, 0, 0)
        mock_validate_source.return_value = "./testpackage"
        mock_validate_python_version.return_value = Version(3, 8, 0)
        mock_validate_keywords.return_value = ["test"]
        mock_validate_dependencies.return_value = []

        result = _validate_publish_inputs(
            name="testpackage",
            version="1.0.0",
            explicit_src_folder_path=None,
            min_python=None,
            keywords=["test"],
            dependencies=[],
        )

        mock_validate_version.assert_called_once_with("1.0.0")
        mock_validate_source.assert_called_once_with("testpackage", None)
        mock_validate_python_version.assert_called_once_with(None)
        mock_validate_keywords.assert_called_once_with(["test"])
        mock_validate_dependencies.assert_called_once_with([])

        self.assertEqual(result[0], Version(1, 0, 0))
        self.assertEqual(result[1], "./testpackage")

    @patch("quickpub.__main__.warning")
    @patch("quickpub.__main__.validate_dependencies")
    @patch("quickpub.__main__.validate_keywords")
    @patch("quickpub.__main__.validate_python_version")
    @patch("quickpub.__main__.validate_source")
    @patch("quickpub.__main__.validate_version")
    def test_warning_on_different_src_path(
        self,
        mock_validate_version,
        mock_validate_source,
        mock_validate_python_version,
        mock_validate_keywords,
        mock_validate_dependencies,
        mock_warning,
    ) -> None:
        mock_validate_version.return_value = Version(1, 0, 0)
        mock_validate_source.return_value = "./different_path"
        mock_validate_python_version.return_value = Version(3, 8, 0)
        mock_validate_keywords.return_value = []
        mock_validate_dependencies.return_value = []

        _validate_publish_inputs(
            name="testpackage",
            version="1.0.0",
            explicit_src_folder_path="./different_path",
            min_python=None,
            keywords=None,
            dependencies=None,
        )

        mock_warning.assert_called_once()

    @patch("quickpub.__main__.validate_dependencies")
    @patch("quickpub.__main__.validate_keywords")
    @patch("quickpub.__main__.validate_python_version")
    @patch("quickpub.__main__.validate_source")
    @patch("quickpub.__main__.validate_version")
    def test_version_object_passed_through(
        self,
        mock_validate_version,
        mock_validate_source,
        mock_validate_python_version,
        mock_validate_keywords,
        mock_validate_dependencies,
    ) -> None:
        version = Version(2, 0, 0)
        mock_validate_version.return_value = version
        mock_validate_source.return_value = "./testpackage"
        mock_validate_python_version.return_value = Version(3, 8, 0)
        mock_validate_keywords.return_value = []
        mock_validate_dependencies.return_value = []

        result = _validate_publish_inputs(
            name="testpackage",
            version=version,
            explicit_src_folder_path=None,
            min_python=None,
            keywords=None,
            dependencies=None,
        )

        self.assertEqual(result[0], version)


class TestRunConstraintEnforcers(BaseTestClass):
    def test_with_enforcers(self) -> None:
        enforcer1 = MagicMock()
        enforcer2 = MagicMock()
        enforcers = [enforcer1, enforcer2]

        _run_constraint_enforcers(
            enforcers=enforcers,
            name="testpackage",
            version=Version(1, 0, 0),
            demo=False,
        )

        enforcer1.enforce.assert_called_once_with(
            name="testpackage", version=Version(1, 0, 0), demo=False
        )
        enforcer2.enforce.assert_called_once_with(
            name="testpackage", version=Version(1, 0, 0), demo=False
        )

    def test_without_enforcers(self) -> None:
        _run_constraint_enforcers(
            enforcers=None, name="testpackage", version=Version(1, 0, 0), demo=False
        )

    def test_with_empty_enforcers_list(self) -> None:
        _run_constraint_enforcers(
            enforcers=[], name="testpackage", version=Version(1, 0, 0), demo=True
        )

    def test_demo_mode(self) -> None:
        enforcer = MagicMock()
        _run_constraint_enforcers(
            enforcers=[enforcer],
            name="testpackage",
            version=Version(1, 0, 0),
            demo=True,
        )
        enforcer.enforce.assert_called_once_with(
            name="testpackage", version=Version(1, 0, 0), demo=True
        )


class TestRunQualityAssurance(BaseTestClass):
    @patch("quickpub.__main__.qa")
    def test_qa_success(self, mock_qa) -> None:
        async def mock_qa_coro():
            return True

        mock_qa.return_value = mock_qa_coro()
        mock_provider = MagicMock()
        mock_pbar = MagicMock()

        _run_quality_assurance(
            python_interpreter_provider=mock_provider,
            global_quality_assurance_runners=[],
            name="testpackage",
            explicit_src_folder_path="./testpackage",
            validated_dependencies=[],
            pbar=mock_pbar,
        )

    @patch("quickpub.__main__.error")
    @patch("quickpub.__main__.qa")
    def test_qa_failure(self, mock_qa, mock_error) -> None:
        async def mock_qa_coro():
            return False

        mock_qa.return_value = mock_qa_coro()
        mock_provider = MagicMock()
        mock_pbar = MagicMock()

        with self.assertRaises(ExitEarlyError):
            _run_quality_assurance(
                python_interpreter_provider=mock_provider,
                global_quality_assurance_runners=[],
                name="testpackage",
                explicit_src_folder_path="./testpackage",
                validated_dependencies=[],
                pbar=mock_pbar,
            )

        mock_error.assert_called_once()

    @patch("quickpub.__main__.qa")
    def test_qa_exit_early_error_propagated(self, mock_qa) -> None:
        async def mock_qa_coro():
            raise ExitEarlyError("QA failed")

        mock_qa.return_value = mock_qa_coro()
        mock_provider = MagicMock()
        mock_pbar = MagicMock()

        with self.assertRaises(ExitEarlyError):
            _run_quality_assurance(
                python_interpreter_provider=mock_provider,
                global_quality_assurance_runners=[],
                name="testpackage",
                explicit_src_folder_path="./testpackage",
                validated_dependencies=[],
                pbar=mock_pbar,
            )

    @patch("quickpub.__main__.qa")
    def test_qa_other_exception_wrapped(self, mock_qa) -> None:
        async def mock_qa_coro():
            raise ValueError("Unexpected error")

        mock_qa.return_value = mock_qa_coro()
        mock_provider = MagicMock()
        mock_pbar = MagicMock()

        with self.assertRaises(RuntimeError) as context:
            _run_quality_assurance(
                python_interpreter_provider=mock_provider,
                global_quality_assurance_runners=[],
                name="testpackage",
                explicit_src_folder_path="./testpackage",
                validated_dependencies=[],
                pbar=mock_pbar,
            )

        self.assertIn("Quality assurance stage has failed", str(context.exception))


class TestCreatePackageFiles(BaseTestClass):
    @patch("quickpub.__main__.create_manifest")
    @patch("quickpub.__main__.create_toml")
    @patch("quickpub.__main__.create_setup")
    def test_all_files_created(
        self, mock_create_setup, mock_create_toml, mock_create_manifest
    ) -> None:
        _create_package_files(
            name="testpackage",
            explicit_src_folder_path="./testpackage",
            readme_file_path="./README.md",
            license_file_path="./LICENSE",
            version=Version(1, 0, 0),
            author="Test Author",
            author_email="test@example.com",
            description="Test description",
            homepage="https://example.com",
            keywords=["test"],
            validated_dependencies=[],
            min_python=Version(3, 8, 0),
            scripts=None,
        )

        mock_create_setup.assert_called_once()
        mock_create_toml.assert_called_once()
        mock_create_manifest.assert_called_once_with(name="testpackage")

    @patch("quickpub.__main__.create_manifest")
    @patch("quickpub.__main__.create_toml")
    @patch("quickpub.__main__.create_setup")
    def test_with_scripts(
        self, mock_create_setup, mock_create_toml, mock_create_manifest
    ) -> None:
        scripts = {"myscript": MagicMock()}
        _create_package_files(
            name="testpackage",
            explicit_src_folder_path="./testpackage",
            readme_file_path="./README.md",
            license_file_path="./LICENSE",
            version=Version(1, 0, 0),
            author="Test Author",
            author_email="test@example.com",
            description="Test description",
            homepage="https://example.com",
            keywords=[],
            validated_dependencies=[],
            min_python=Version(3, 8, 0),
            scripts=scripts,
        )

        call_args = mock_create_toml.call_args
        self.assertEqual(call_args.kwargs["scripts"], scripts)


class TestBuildAndUploadPackages(BaseTestClass):
    def test_demo_mode_skips_build_and_upload(self) -> None:
        build_schema = MagicMock()
        upload_target = MagicMock()

        _build_and_upload_packages(
            build_schemas=[build_schema],
            upload_targets=[upload_target],
            name="testpackage",
            version=Version(1, 0, 0),
            demo=True,
        )

        build_schema.build.assert_not_called()
        upload_target.upload.assert_not_called()

    def test_normal_mode_builds_and_uploads(self) -> None:
        build_schema = MagicMock()
        upload_target = MagicMock()

        _build_and_upload_packages(
            build_schemas=[build_schema],
            upload_targets=[upload_target],
            name="testpackage",
            version=Version(1, 0, 0),
            demo=False,
        )

        build_schema.build.assert_called_once()
        upload_target.upload.assert_called_once_with(
            name="testpackage", version=Version(1, 0, 0)
        )

    def test_multiple_schemas_and_targets(self) -> None:
        build_schema1 = MagicMock()
        build_schema2 = MagicMock()
        upload_target1 = MagicMock()
        upload_target2 = MagicMock()

        _build_and_upload_packages(
            build_schemas=[build_schema1, build_schema2],
            upload_targets=[upload_target1, upload_target2],
            name="testpackage",
            version=Version(1, 0, 0),
            demo=False,
        )

        build_schema1.build.assert_called_once()
        build_schema2.build.assert_called_once()
        upload_target1.upload.assert_called_once()
        upload_target2.upload.assert_called_once()


class TestPublish(BaseTestClass):
    @patch("quickpub.__main__._build_and_upload_packages")
    @patch("quickpub.__main__._create_package_files")
    @patch("quickpub.__main__._run_quality_assurance")
    @patch("quickpub.__main__._run_constraint_enforcers")
    @patch("quickpub.__main__._validate_publish_inputs")
    @patch("quickpub.__main__.logger")
    def test_publish_success(
        self,
        mock_logger,
        mock_validate,
        mock_enforcers,
        mock_qa,
        mock_create_files,
        mock_build_upload,
    ) -> None:
        mock_validate.return_value = (
            Version(1, 0, 0),
            "./testpackage",
            Version(3, 8, 0),
            [],
            [],
        )

        build_schema = MagicMock()
        upload_target = MagicMock()

        publish(
            name="testpackage",
            author="Test Author",
            author_email="test@example.com",
            description="Test description",
            homepage="https://example.com",
            build_schemas=[build_schema],
            upload_targets=[upload_target],
        )

        mock_validate.assert_called_once()
        mock_enforcers.assert_called_once()
        mock_qa.assert_called_once()
        mock_create_files.assert_called_once()
        mock_build_upload.assert_called_once()

    @patch("quickpub.__main__._build_and_upload_packages")
    @patch("quickpub.__main__._create_package_files")
    @patch("quickpub.__main__._run_quality_assurance")
    @patch("quickpub.__main__._run_constraint_enforcers")
    @patch("quickpub.__main__._validate_publish_inputs")
    @patch("quickpub.__main__.logger")
    def test_publish_logs_elapsed_time(
        self,
        mock_logger,
        mock_validate,
        mock_enforcers,
        mock_qa,
        mock_create_files,
        mock_build_upload,
    ) -> None:
        mock_validate.return_value = (
            Version(1, 0, 0),
            "./testpackage",
            Version(3, 8, 0),
            [],
            [],
        )

        publish(
            name="testpackage",
            author="Test Author",
            author_email="test@example.com",
            description="Test description",
            homepage="https://example.com",
            build_schemas=[],
            upload_targets=[],
        )

        info_calls = [str(call) for call in mock_logger.info.call_args_list]
        elapsed_logged = any("Publish finished" in str(call) for call in info_calls)
        self.assertTrue(elapsed_logged)

    @patch("quickpub.__main__._build_and_upload_packages")
    @patch("quickpub.__main__._create_package_files")
    @patch("quickpub.__main__._run_quality_assurance")
    @patch("quickpub.__main__._run_constraint_enforcers")
    @patch("quickpub.__main__._validate_publish_inputs")
    def test_publish_demo_mode(
        self,
        mock_validate,
        mock_enforcers,
        mock_qa,
        mock_create_files,
        mock_build_upload,
    ) -> None:
        mock_validate.return_value = (
            Version(1, 0, 0),
            "./testpackage",
            Version(3, 8, 0),
            [],
            [],
        )

        publish(
            name="testpackage",
            author="Test Author",
            author_email="test@example.com",
            description="Test description",
            homepage="https://example.com",
            build_schemas=[],
            upload_targets=[],
            demo=True,
        )

        call_args = mock_build_upload.call_args
        self.assertTrue(call_args.kwargs["demo"])


class TestMain(BaseTestClass):
    @patch("quickpub.__main__.fire.Fire")
    def test_main_calls_fire(self, mock_fire) -> None:
        main()
        mock_fire.assert_called_once_with(publish)


if __name__ == "__main__":
    unittest.main()
