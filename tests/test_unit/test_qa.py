import asyncio
import unittest
from typing import Any, AsyncIterator
from unittest.mock import patch, MagicMock, AsyncMock

from quickpub import ExitEarlyError, Version, Dependency
from quickpub.qa import (
    global_import_sanity_check,
    _get_installed_packages,
    _check_dependency_satisfaction,
    validate_dependencies,
    run_config,
    _setup_qa_environment,
    _submit_qa_tasks,
    _execute_qa_tasks,
    qa,
    is_task_run_success,
    VERSION_REGEX,
)

from tests.base_test_classes import AsyncBaseTestClass


class TestGlobalImportSanityCheck(AsyncBaseTestClass):
    async def test_success(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.append(False)

        executor = AsyncMock()
        executor.return_value = (0, [], [])

        pbar = MagicMock()

        await global_import_sanity_check(
            package_name="testpackage",
            executor=executor,
            is_system_interpreter=False,
            env_name="testenv",
            task_id=0,
            pbar=pbar,
        )

        self.assertTrue(is_task_run_success[0])
        pbar.update.assert_called_once_with(1)

    async def test_failure(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.append(False)

        executor = AsyncMock()
        executor.return_value = (1, [], ["error message"])

        pbar = MagicMock()

        with self.assertRaises(ExitEarlyError):
            await global_import_sanity_check(
                package_name="testpackage",
                executor=executor,
                is_system_interpreter=False,
                env_name="testenv",
                task_id=0,
                pbar=pbar,
            )

        self.assertFalse(is_task_run_success[0])
        pbar.update.assert_called_once_with(1)

    async def test_exception_handling(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.append(False)

        executor = AsyncMock()
        executor.side_effect = ValueError("Unexpected error")

        pbar = MagicMock()

        with self.assertRaises(ValueError):
            await global_import_sanity_check(
                package_name="testpackage",
                executor=executor,
                is_system_interpreter=False,
                env_name="testenv",
                task_id=0,
                pbar=pbar,
            )

        self.assertFalse(is_task_run_success[0])
        pbar.update.assert_called_once_with(1)

    async def test_system_interpreter(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.append(False)

        executor = AsyncMock()
        executor.return_value = (0, [], [])

        await global_import_sanity_check(
            package_name="testpackage",
            executor=executor,
            is_system_interpreter=True,
            env_name="testenv",
            task_id=0,
            pbar=None,
        )

        call_args = executor.call_args[0][0]
        self.assertIn("python", call_args.lower())


class TestGetInstalledPackages(AsyncBaseTestClass):
    async def test_parse_pip_list_output(self) -> None:
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

        result = await _get_installed_packages(executor, "testenv")

        self.assertIn("package1", result)
        self.assertIsInstance(result["package1"], Dependency)
        pkg1 = result["package1"]
        assert isinstance(pkg1, Dependency)
        self.assertEqual(pkg1.ver, Version(1, 0, 0))

        self.assertIn("package2", result)
        self.assertIsInstance(result["package2"], Dependency)

        self.assertIn("package3", result)
        self.assertEqual(result["package3"], "invalid")

    async def test_pip_list_failure(self) -> None:
        executor = AsyncMock()
        executor.return_value = (1, [], ["error"])

        with self.assertRaises(ExitEarlyError):
            await _get_installed_packages(executor, "testenv")

    async def test_empty_pip_list(self) -> None:
        executor = AsyncMock()
        executor.return_value = (0, ["Package    Version", "---------- -------"], [])

        result = await _get_installed_packages(executor, "testenv")
        self.assertEqual(len(result), 0)


class TestCheckDependencySatisfaction(unittest.TestCase):
    def test_all_satisfied(self) -> None:
        from typing import Dict, Union

        required = [Dependency("pkg1", ">=", Version(1, 0, 0))]
        installed: Dict[str, Union[str, Dependency]] = {
            "pkg1": Dependency("pkg1", "==", Version(2, 0, 0))
        }

        result = _check_dependency_satisfaction(required, installed)
        self.assertEqual(len(result), 0)

    def test_missing_dependency(self) -> None:
        from typing import Dict, Union

        required = [Dependency("pkg1", ">=", Version(1, 0, 0))]
        installed: Dict[str, Union[str, Dependency]] = {}

        result = _check_dependency_satisfaction(required, installed)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0].name, "pkg1")
        self.assertEqual(result[0][1], "dependency not found")

    def test_version_mismatch(self) -> None:
        from typing import Dict, Union

        required = [Dependency("pkg1", ">=", Version(2, 0, 0))]
        installed: Dict[str, Union[str, Dependency]] = {
            "pkg1": Dependency("pkg1", "==", Version(1, 0, 0))
        }

        result = _check_dependency_satisfaction(required, installed)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Invalid version installed")

    def test_unsupported_format(self) -> None:
        from typing import Dict, Union

        required = [Dependency("pkg1", ">=", Version(1, 0, 0))]
        installed: Dict[str, Union[str, Dependency]] = {"pkg1": "unsupported format"}

        result = _check_dependency_satisfaction(required, installed)
        self.assertEqual(len(result), 1)
        self.assertIn("not currently supported", result[0][1])


class TestValidateDependencies(AsyncBaseTestClass):
    async def test_success(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.append(False)

        executor = AsyncMock()
        executor.return_value = (
            0,
            [
                "Package    Version",
                "---------- -------",
                "pkg1       2.0.0",
            ],
            [],
        )

        required = [Dependency("pkg1", ">=", Version(1, 0, 0))]
        pbar = MagicMock()

        await validate_dependencies(
            validation_exit_on_fail=True,
            required_dependencies=required,
            executor=executor,
            env_name="testenv",
            task_id=0,
            pbar=pbar,
        )

        self.assertTrue(is_task_run_success[0])
        pbar.update.assert_called_once_with(1)

    async def test_failure_exit_on_fail(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.append(False)

        executor = AsyncMock()
        executor.return_value = (
            0,
            [
                "Package    Version",
                "---------- -------",
            ],
            [],
        )

        required = [Dependency("pkg1", ">=", Version(1, 0, 0))]
        pbar = MagicMock()

        with self.assertRaises(ExitEarlyError):
            await validate_dependencies(
                validation_exit_on_fail=True,
                required_dependencies=required,
                executor=executor,
                env_name="testenv",
                task_id=0,
                pbar=pbar,
            )

        self.assertFalse(is_task_run_success[0])

    async def test_exception_handling(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.append(False)

        executor = AsyncMock()
        executor.side_effect = ValueError("Unexpected error")

        pbar = MagicMock()

        with self.assertRaises(ValueError):
            await validate_dependencies(
                validation_exit_on_fail=True,
                required_dependencies=[],
                executor=executor,
                env_name="testenv",
                task_id=0,
                pbar=pbar,
            )

        self.assertFalse(is_task_run_success[0])


class TestRunConfig(AsyncBaseTestClass):
    async def test_success(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.append(False)

        runner = MagicMock()
        runner.run = AsyncMock()

        executor = AsyncMock()

        pbar = MagicMock()

        await run_config(
            env_name="testenv",
            async_executor=executor,
            runner=runner,
            config_id=1,
            task_id=0,
            is_system_interpreter=False,
            validation_exit_on_fail=True,
            src_folder_path="./testpackage",
            pbar=pbar,
        )

        self.assertTrue(is_task_run_success[0])
        runner.run.assert_called_once()
        pbar.update.assert_called_once_with(1)

    async def test_exit_early_error(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.append(False)

        runner = MagicMock()
        runner.run = AsyncMock(side_effect=ExitEarlyError("QA failed"))

        executor = AsyncMock()
        pbar = MagicMock()

        with self.assertRaises(ExitEarlyError):
            await run_config(
                env_name="testenv",
                async_executor=executor,
                runner=runner,
                config_id=1,
                task_id=0,
                is_system_interpreter=False,
                validation_exit_on_fail=True,
                src_folder_path="./testpackage",
                pbar=pbar,
            )

        self.assertFalse(is_task_run_success[0])

    async def test_other_exception_with_exit_on_fail(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.append(False)

        runner = MagicMock()
        runner.run = AsyncMock(side_effect=ValueError("Unexpected error"))

        executor = AsyncMock()
        pbar = MagicMock()

        with self.assertRaises(RuntimeError):
            await run_config(
                env_name="testenv",
                async_executor=executor,
                runner=runner,
                config_id=1,
                task_id=0,
                is_system_interpreter=False,
                validation_exit_on_fail=True,
                src_folder_path="./testpackage",
                pbar=pbar,
            )

        self.assertFalse(is_task_run_success[0])

    async def test_other_exception_without_exit_on_fail(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.append(False)

        runner = MagicMock()
        runner.run = AsyncMock(side_effect=ValueError("Unexpected error"))

        executor = AsyncMock()
        pbar = MagicMock()

        await run_config(
            env_name="testenv",
            async_executor=executor,
            runner=runner,
            config_id=1,
            task_id=0,
            is_system_interpreter=False,
            validation_exit_on_fail=False,
            src_folder_path="./testpackage",
            pbar=pbar,
        )

        self.assertFalse(is_task_run_success[0])


class TestSetupQaEnvironment(unittest.TestCase):
    def test_default_python_provider(self) -> None:
        from quickpub.strategies import DefaultPythonProvider

        provider = DefaultPythonProvider()
        result = _setup_qa_environment(provider)
        self.assertTrue(result)

    def test_non_default_python_provider(self) -> None:
        provider = MagicMock()
        result = _setup_qa_environment(provider)
        self.assertFalse(result)


class TestSubmitQaTasks(AsyncBaseTestClass):
    async def test_submit_tasks(self) -> None:
        is_task_run_success.clear()

        async def mock_provider_iter() -> AsyncIterator[tuple[str, Any]]:
            from typing import AsyncIterator, Any

            executor = AsyncMock()
            executor.__enter__ = AsyncMock(return_value=executor)
            executor.__exit__ = AsyncMock(return_value=None)
            executor.prev = None
            yield ("env1", executor)

        provider = MagicMock()
        provider.exit_on_fail = True
        provider.__aiter__ = lambda self: mock_provider_iter()  # type: ignore[assignment]

        pool = MagicMock()
        pool.submit = AsyncMock()

        pbar = MagicMock()

        total = await _submit_qa_tasks(
            python_provider=provider,
            quality_assurance_strategies=[],
            package_name="testpackage",
            src_folder_path="./testpackage",
            dependencies=[],
            is_system_interpreter=False,
            pool=pool,
            pbar=pbar,
        )

        self.assertGreater(total, 0)
        self.assertEqual(len(is_task_run_success), total)


class TestExecuteQaTasks(AsyncBaseTestClass):
    async def test_all_success(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.extend([True, True, True])

        pool = MagicMock()
        pool.start = AsyncMock()
        pool.join = AsyncMock()

        result = await _execute_qa_tasks(pool, total=3, qa_start_time=0.0)

        self.assertTrue(result)
        pool.start.assert_called_once()
        pool.join.assert_called_once()

    async def test_some_failures(self) -> None:
        is_task_run_success.clear()
        is_task_run_success.extend([True, False, True])

        pool = MagicMock()
        pool.start = AsyncMock()
        pool.join = AsyncMock()

        result = await _execute_qa_tasks(pool, total=3, qa_start_time=0.0)

        self.assertFalse(result)


class TestQa(AsyncBaseTestClass):
    @patch("quickpub.qa._execute_qa_tasks")
    @patch("quickpub.qa._submit_qa_tasks")
    @patch("quickpub.qa.WorkerPool")
    @patch("quickpub.qa._setup_qa_environment")
    async def test_qa_workflow(
        self, mock_setup, mock_worker_pool, mock_submit, mock_execute
    ) -> None:
        is_task_run_success.clear()

        mock_setup.return_value = False
        mock_worker_pool.return_value = MagicMock()
        mock_submit.return_value = 5
        mock_execute.return_value = True

        from quickpub.strategies import QualityAssuranceRunner

        provider = MagicMock()
        runners: list[QualityAssuranceRunner] = []

        result = await qa(
            python_provider=provider,
            quality_assurance_strategies=runners,
            package_name="testpackage",
            src_folder_path="./testpackage",
            dependencies=[],
            pbar=None,
        )

        self.assertTrue(result)
        mock_setup.assert_called_once_with(provider)
        mock_submit.assert_called_once()
        mock_execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
