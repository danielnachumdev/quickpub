from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from quickpub import (
    DefaultPythonProvider,
    PipPackageManager,
    UvPackageManager,
    UvPythonProvider,
    resolve_publish_environment,
)
from quickpub.__main__ import publish
from quickpub.qa import qa
from quickpub.structures import Version

from tests.integration.conftest import PACKAGE_NAME, use_project_root


@pytest.mark.integration
def test_mock_pip_project_uses_pip_and_system_python(mock_pip_project: Path) -> None:
    package_manager, provider = resolve_publish_environment(mock_pip_project)

    assert isinstance(package_manager, PipPackageManager)
    assert isinstance(provider, DefaultPythonProvider)


@pytest.mark.integration
def test_mock_uv_project_uses_uv_environment(mock_uv_project: Path) -> None:
    package_manager, provider = resolve_publish_environment(mock_uv_project)

    assert isinstance(package_manager, UvPackageManager)
    assert isinstance(provider, UvPythonProvider)
    assert package_manager.project_root == mock_uv_project
    assert provider.project_root == mock_uv_project


@pytest.mark.integration
@pytest.mark.asyncio
async def test_qa_succeeds_in_mock_pip_project(mock_pip_project: Path) -> None:
    with use_project_root(mock_pip_project):
        package_manager, provider = resolve_publish_environment(mock_pip_project)
        package_dir = mock_pip_project / PACKAGE_NAME

        result = await qa(
            python_provider=provider,
            quality_assurance_strategies=[],
            package_name=PACKAGE_NAME,
            src_folder_path=str(package_dir),
            dependencies=[],
            package_manager=package_manager,
        )

    assert result is True


@pytest.mark.integration
@pytest.mark.asyncio
@patch(
    "quickpub.strategies.implementations.package_managers.uv_package_manager.UvPackageManager.prepare",
    new_callable=AsyncMock,
)
async def test_qa_succeeds_in_mock_uv_project(
    mock_prepare: AsyncMock,
    mock_uv_project: Path,
) -> None:
    with use_project_root(mock_uv_project):
        package_manager, provider = resolve_publish_environment(mock_uv_project)
        package_dir = mock_uv_project / PACKAGE_NAME

        result = await qa(
            python_provider=provider,
            quality_assurance_strategies=[],
            package_name=PACKAGE_NAME,
            src_folder_path=str(package_dir),
            dependencies=[],
            package_manager=package_manager,
        )

    mock_prepare.assert_called()
    assert result is True


@pytest.mark.integration
@patch("quickpub.__main__._build_and_upload_packages")
@patch("quickpub.__main__._create_package_files")
@patch("quickpub.__main__._run_constraint_enforcers")
@patch("quickpub.__main__._validate_publish_inputs")
def test_publish_auto_resolves_pip_project_environment(
    mock_validate,
    mock_enforcers,
    mock_create_files,
    mock_build_upload,
    mock_pip_project: Path,
) -> None:
    mock_validate.return_value = (
        Version(1, 0, 0),
        str(mock_pip_project / PACKAGE_NAME),
        Version(3, 8, 0),
        [],
        [],
    )

    with patch("quickpub.__main__._run_quality_assurance") as mock_qa:
        publish(
            name=PACKAGE_NAME,
            author="Test Author",
            author_email="test@example.com",
            description="Test description",
            homepage="https://example.com",
            build_schemas=[MagicMock()],
            upload_targets=[MagicMock()],
            project_root=mock_pip_project,
            demo=True,
        )

        mock_qa.assert_called_once()
        assert isinstance(mock_qa.call_args.args[6], PipPackageManager)


@pytest.mark.integration
@patch("quickpub.__main__._build_and_upload_packages")
@patch("quickpub.__main__._create_package_files")
@patch("quickpub.__main__._run_constraint_enforcers")
@patch("quickpub.__main__._validate_publish_inputs")
def test_publish_auto_resolves_uv_project_environment(
    mock_validate,
    mock_enforcers,
    mock_create_files,
    mock_build_upload,
    mock_uv_project: Path,
) -> None:
    mock_validate.return_value = (
        Version(1, 0, 0),
        str(mock_uv_project / PACKAGE_NAME),
        Version(3, 8, 0),
        [],
        [],
    )

    with patch("quickpub.__main__._run_quality_assurance") as mock_qa:
        publish(
            name=PACKAGE_NAME,
            author="Test Author",
            author_email="test@example.com",
            description="Test description",
            homepage="https://example.com",
            build_schemas=[MagicMock()],
            upload_targets=[MagicMock()],
            project_root=mock_uv_project,
            demo=True,
        )

        mock_qa.assert_called_once()
        assert isinstance(mock_qa.call_args.args[6], UvPackageManager)
