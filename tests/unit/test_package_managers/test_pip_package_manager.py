from unittest.mock import AsyncMock

from quickpub import ExitEarlyError, Version
from quickpub.strategies.implementations.package_managers.pip_package_manager import (
    PipPackageManager,
)
from quickpub.structures import Dependency

from tests.common.base_test_classes import AsyncBaseTestClass


class TestPipPackageManager(AsyncBaseTestClass):
    async def test_prepare_is_no_op(self) -> None:
        executor = AsyncMock()
        manager = PipPackageManager()

        await manager.prepare(executor)

        executor.assert_not_called()

    async def test_list_installed_calls_pip_list(self) -> None:
        executor = AsyncMock()
        executor.return_value = (
            0,
            [
                "Package    Version",
                "---------- -------",
                "package1   1.0.0",
                "package2   2.0.0",
                "package3   invalid",
            ],
            [],
        )
        manager = PipPackageManager()

        result = await manager.list_installed(executor, "testenv")

        executor.assert_called_once_with("pip list")
        self.assertIn("package1", result)
        self.assertIsInstance(result["package1"], Dependency)
        pkg1 = result["package1"]
        assert isinstance(pkg1, Dependency)
        self.assertEqual(pkg1.ver, Version(1, 0, 0))
        self.assertEqual(result["package3"], "invalid")

    async def test_list_installed_failure_raises(self) -> None:
        executor = AsyncMock()
        executor.return_value = (1, [], ["error"])
        manager = PipPackageManager()

        with self.assertRaises(ExitEarlyError):
            await manager.list_installed(executor, "testenv")

    async def test_install_command(self) -> None:
        manager = PipPackageManager()
        self.assertEqual(manager.install_command("pytest"), "pip install pytest")

    async def test_show_command(self) -> None:
        manager = PipPackageManager()
        self.assertEqual(
            manager.show_command("pytest-xdist"), "pip show pytest-xdist"
        )

    async def test_wrap_command_is_pass_through(self) -> None:
        manager = PipPackageManager()
        command = "python -m pytest ./tests"
        self.assertEqual(manager.wrap_command(command), command)
