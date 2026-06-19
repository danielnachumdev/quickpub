from pathlib import Path
from unittest.mock import AsyncMock

from quickpub import ExitEarlyError
from quickpub.strategies.implementations.package_managers.uv_package_manager import (
    UvPackageManager,
)

from tests.base_test_classes import AsyncBaseTestClass


class TestUvPackageManager(AsyncBaseTestClass):
    async def test_prepare_runs_uv_sync(self) -> None:
        project_root = Path("/tmp/quickpub-uv-test")
        lockfile = project_root / "uv.lock"
        lockfile.parent.mkdir(parents=True, exist_ok=True)
        lockfile.write_text("", encoding="utf-8")
        executor = AsyncMock()
        executor.return_value = (0, [], [])
        manager = UvPackageManager(project_root=project_root)

        await manager.prepare(executor)

        executor.assert_called_once_with("uv sync")

    async def test_prepare_fails_without_uv_lock(self) -> None:
        project_root = Path("/tmp/quickpub-uv-no-lock")
        executor = AsyncMock()
        manager = UvPackageManager(project_root=project_root)

        with self.assertRaises(ExitEarlyError):
            await manager.prepare(executor)

        executor.assert_not_called()

    async def test_list_installed_calls_uv_pip_list(self) -> None:
        executor = AsyncMock()
        executor.return_value = (
            0,
            [
                "Package    Version",
                "---------- -------",
                "pytest     8.0.0",
            ],
            [],
        )
        manager = UvPackageManager(project_root=Path("."))

        await manager.list_installed(executor, "uv")

        executor.assert_called_once_with("uv pip list")

    async def test_install_command(self) -> None:
        manager = UvPackageManager(project_root=Path("."))
        self.assertEqual(manager.install_command("mypy"), "uv add --dev mypy")

    async def test_show_command(self) -> None:
        manager = UvPackageManager(project_root=Path("."))
        self.assertEqual(
            manager.show_command("pytest-xdist"), "uv pip show pytest-xdist"
        )

    async def test_wrap_command_prefixes_uv_run(self) -> None:
        manager = UvPackageManager(project_root=Path("."))
        command = "python -m pytest ./tests"
        self.assertEqual(
            manager.wrap_command(command), "uv run -- python -m pytest ./tests"
        )
