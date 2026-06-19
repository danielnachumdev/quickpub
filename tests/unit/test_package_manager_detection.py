from pathlib import Path
from unittest.mock import patch

from quickpub.package_manager_detection import (
    detect_package_manager,
    resolve_publish_environment,
)
from quickpub.strategies.implementations.package_managers.pip_package_manager import (
    PipPackageManager,
)
from quickpub.strategies.implementations.package_managers.uv_package_manager import (
    UvPackageManager,
)
from quickpub.strategies.implementations.python_providers.default_python_provider import (
    DefaultPythonProvider,
)
from quickpub.strategies.implementations.python_providers.uv_python_provider import (
    UvPythonProvider,
)

from tests.common.base_test_classes import BaseTestClass
from tests.common.helpers import temporary_test_directory


class TestDetectPackageManager(BaseTestClass):
    def test_returns_uv_when_lockfile_present(self) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "uv.lock").write_text("", encoding="utf-8")

            manager = detect_package_manager(tmp_dir)

            self.assertIsInstance(manager, UvPackageManager)
            self.assertEqual(manager.project_root, tmp_dir)

    def test_returns_pip_when_lockfile_absent(self) -> None:
        with temporary_test_directory() as tmp_dir:
            manager = detect_package_manager(tmp_dir)

            self.assertIsInstance(manager, PipPackageManager)


class TestResolvePublishEnvironment(BaseTestClass):
    def test_auto_resolves_uv_when_lockfile_present(self) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "uv.lock").write_text("", encoding="utf-8")

            package_manager, python_provider = resolve_publish_environment(tmp_dir)

            self.assertIsInstance(package_manager, UvPackageManager)
            self.assertIsInstance(python_provider, UvPythonProvider)
            self.assertEqual(package_manager.project_root, tmp_dir)
            self.assertEqual(python_provider.project_root, tmp_dir)

    def test_auto_resolves_pip_when_lockfile_absent(self) -> None:
        with temporary_test_directory() as tmp_dir:
            package_manager, python_provider = resolve_publish_environment(tmp_dir)

            self.assertIsInstance(package_manager, PipPackageManager)
            self.assertIsInstance(python_provider, DefaultPythonProvider)

    def test_explicit_provider_is_preserved(self) -> None:
        with temporary_test_directory() as tmp_dir:
            explicit_provider = DefaultPythonProvider()

            package_manager, python_provider = resolve_publish_environment(
                tmp_dir,
                python_interpreter_provider=explicit_provider,
            )

            self.assertIs(python_provider, explicit_provider)
            self.assertIsInstance(package_manager, PipPackageManager)

    def test_explicit_package_manager_selects_matching_provider(self) -> None:
        with temporary_test_directory() as tmp_dir:
            explicit_manager = UvPackageManager(project_root=tmp_dir)

            package_manager, python_provider = resolve_publish_environment(
                tmp_dir,
                package_manager=explicit_manager,
            )

            self.assertIs(package_manager, explicit_manager)
            self.assertIsInstance(python_provider, UvPythonProvider)

    def test_explicit_both_are_preserved(self) -> None:
        with temporary_test_directory() as tmp_dir:
            explicit_manager = PipPackageManager()
            explicit_provider = DefaultPythonProvider()

            package_manager, python_provider = resolve_publish_environment(
                tmp_dir,
                python_interpreter_provider=explicit_provider,
                package_manager=explicit_manager,
            )

            self.assertIs(package_manager, explicit_manager)
            self.assertIs(python_provider, explicit_provider)
