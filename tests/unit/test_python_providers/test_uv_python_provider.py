from pathlib import Path

from quickpub.strategies.implementations.package_managers.uv_package_manager import (
    UvPackageManager,
)
from quickpub.strategies.implementations.python_providers.uv_python_provider import (
    UvPythonProvider,
)

from tests.base_test_classes import AsyncBaseTestClass, BaseTestClass


class TestUvPythonProviderSync(BaseTestClass):
    def test_exposes_uv_package_manager(self) -> None:
        project_root = Path("/tmp/quickpub-uv-provider-manager")
        provider = UvPythonProvider(project_root=project_root)

        self.assertIsInstance(provider.package_manager, UvPackageManager)
        self.assertEqual(provider.package_manager.project_root, project_root)

    def test_get_python_executable_name_points_to_venv(self) -> None:
        project_root = Path("/tmp/quickpub-uv-provider-exec")
        provider = UvPythonProvider(project_root=project_root)

        executable = provider.get_python_executable_name()

        self.assertIn(".venv", executable)
        self.assertIn("python", executable)


class TestUvPythonProvider(AsyncBaseTestClass):
    async def test_yields_single_uv_environment(self) -> None:
        project_root = Path("/tmp/quickpub-uv-provider")
        lockfile = project_root / "uv.lock"
        lockfile.parent.mkdir(parents=True, exist_ok=True)
        lockfile.write_text("", encoding="utf-8")
        provider = UvPythonProvider(project_root=project_root)

        results = []
        async for env_name, executor in provider:
            results.append(env_name)

        self.assertEqual(["uv"], results)
