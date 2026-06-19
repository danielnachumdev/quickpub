import unittest
from unittest.mock import Mock, patch

from quickpub import DefaultPythonProvider, PytestRunner, ExitEarlyError

from tests.base_test_classes import AsyncBaseTestClass, BaseTestClass
from tests.test_helpers import temporary_test_directory

TEST_FILE_PATH: str = "test_foo.py"


class TestPytestRunner(AsyncBaseTestClass):
    async def _setup_provider(self) -> tuple:
        """Helper method to set up the Python provider."""
        async for name, base in DefaultPythonProvider():
            base.prev = None
            return name, base
        raise RuntimeError("No Python provider found")

    async def test_default_no_tests(self) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = PytestRunner(bound=">0.8", no_tests_score=0, target=str(tmp_dir))
            with base:  # type: ignore
                with self.assertRaises(RuntimeError) as e:
                    await runner.run(
                        target=str(tmp_dir),
                        executor=base,  # type: ignore
                        env_name=env_name,  # type: ignore
                    )
                self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_default_empty_tests(self) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import pytest
            """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = PytestRunner(bound=">0.8", no_tests_score=0, target=str(tmp_dir))
            with base:  # type: ignore
                with self.assertRaises(RuntimeError) as e:
                    await runner.run(
                        target=str(tmp_dir),
                        executor=base,  # type: ignore
                        env_name=env_name,  # type: ignore
                    )
                self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_only_one_test_that_passes(self) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import pytest
        
def test_add():
    assert 1 + 1 == 2        
                    """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = PytestRunner(bound=">0.8", no_tests_score=0, target=str(tmp_dir))
            with base:  # type: ignore
                # Should complete without raising an exception since 1 passing test = score 1.0 > 0.8
                await runner.run(
                    target=str(tmp_dir),
                    executor=base,  # type: ignore
                    env_name=env_name,  # type: ignore
                )

    async def test_only_one_test_that_fails(self) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import pytest

def test_add():
    assert 1 + 1 == 1        
                    """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = PytestRunner(bound=">0.8", no_tests_score=0, target=str(tmp_dir))
            with base:  # type: ignore
                with self.assertRaises(RuntimeError) as e:
                    await runner.run(
                        target=str(tmp_dir),
                        executor=base,  # type: ignore
                        env_name=env_name,  # type: ignore
                    )
                self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_combined(self) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import pytest

def test_add():
    assert 1 + 1 == 1  
    
def test_add2():
    assert 1 + 1 == 2        
                            """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = PytestRunner(bound=">=0", no_tests_score=0, target=str(tmp_dir))
            with base:  # type: ignore
                await runner.run(
                    target=str(tmp_dir),
                    executor=base,  # type: ignore
                    env_name=env_name,  # type: ignore
                )

    async def test_combined_with_bound_should_fail(self) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import pytest

def test_add():
    assert 1 + 1 == 1  
    
def test_add2():
    assert 1 + 1 == 2        
                            """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = PytestRunner(bound=">0.8", no_tests_score=0, target=str(tmp_dir))
            with base:  # type: ignore
                with self.assertRaises(RuntimeError) as e:
                    await runner.run(
                        target=str(tmp_dir),
                        executor=base,  # type: ignore
                        env_name=env_name,  # type: ignore
                    )
                self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_combined_with_bound_should_pass(self) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import pytest

def test_add():
    assert 1 + 1 == 1  
    
def test_add2():
    assert 1 + 1 == 2         
                            """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = PytestRunner(bound=">=0.5", no_tests_score=0, target=str(tmp_dir))
            with base:  # type: ignore
                await runner.run(
                    target=str(tmp_dir),
                    executor=base,  # type: ignore
                    env_name=env_name,  # type: ignore
                )


class TestPytestRunnerBuildCommand(BaseTestClass):

    @patch(
        "quickpub.strategies.implementations.quality_assurance_runners.pytest_qa_runner.subprocess.run"
    )
    def test_build_command_uses_xdist_when_available(self, mock_run) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            mock_run.return_value = Mock(returncode=0)
            runner = PytestRunner()

            command = runner._build_command(target=str(tmp_dir / "tests"))

            self.assertIn("-n auto", command)
            mock_run.assert_called_once()

    @patch(
        "quickpub.strategies.implementations.quality_assurance_runners.pytest_qa_runner.subprocess.run"
    )
    def test_build_command_skips_xdist_when_missing(self, mock_run) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            mock_run.return_value = Mock(returncode=1)
            runner = PytestRunner()

            command = runner._build_command(target=str(tmp_dir / "tests"))

            self.assertNotIn("-n auto", command)
            mock_run.assert_called_once()

    @patch(
        "quickpub.strategies.implementations.quality_assurance_runners.pytest_qa_runner.subprocess.run"
    )
    def test_build_command_respects_configured_workers(self, mock_run) -> None:
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            mock_run.return_value = Mock(returncode=0)
            runner = PytestRunner(xdist_workers=4)

            command = runner._build_command(target=str(tmp_dir / "tests"))

            self.assertIn("-n 4", command)
            mock_run.assert_called_once()


class TestPytestRunnerPackageManager(BaseTestClass):
    @patch(
        "quickpub.strategies.implementations.quality_assurance_runners.pytest_qa_runner.subprocess.run"
    )
    def test_build_command_wraps_with_uv_package_manager(self, mock_run) -> None:
        from pathlib import Path
        from unittest.mock import MagicMock

        from quickpub.strategies.implementations.package_managers.uv_package_manager import (
            UvPackageManager,
        )

        mock_run.return_value = Mock(returncode=1)
        package_manager = UvPackageManager(project_root=Path("."))
        runner = PytestRunner(package_manager=package_manager)

        command = runner._build_command(target="./tests")
        wrapped_command = runner.package_manager.wrap_command(command)

        self.assertTrue(wrapped_command.startswith("uv run --"))

    @patch(
        "quickpub.strategies.implementations.quality_assurance_runners.pytest_qa_runner.subprocess.run"
    )
    def test_is_xdist_installed_uses_package_manager_show_command(self, mock_run) -> None:
        from unittest.mock import MagicMock

        package_manager = MagicMock()
        package_manager.show_command.return_value = "uv pip show pytest-xdist"
        mock_run.return_value = Mock(returncode=0)
        runner = PytestRunner(package_manager=package_manager)

        installed = runner._is_xdist_installed()

        package_manager.show_command.assert_called_once_with("pytest-xdist")
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args, "uv pip show pytest-xdist")
        self.assertTrue(installed)

    def test_install_dependencies_uses_package_manager(self) -> None:
        from unittest.mock import MagicMock

        package_manager = MagicMock()
        package_manager.install_command.return_value = "uv add --dev pytest"
        runner = PytestRunner(package_manager=package_manager)
        base = MagicMock()
        base.__enter__ = MagicMock(return_value=base)
        base.__exit__ = MagicMock(return_value=False)

        runner._install_dependencies(base)

        package_manager.install_command.assert_called_once_with("pytest")
        base.assert_called_once_with("uv add --dev pytest")
