import unittest
from unittest.mock import Mock, patch

from danielutils import create_file, AutoCWDTestCase, AsyncAutoCWDTestCase

from quickpub import DefaultPythonProvider, PytestRunner, ExitEarlyError

TEST_FILE_PATH: str = "./test_foo.py"


class TestPytestRunner(AsyncAutoCWDTestCase):
    async def asyncSetUp(self):
        async for name, base in DefaultPythonProvider():
            base.prev = None
            self.env_name, self.base = name, base
            break
        self.base._instance_flush_stdout = False
        self.base._instance_flush_stderr = False
        create_file("./__init__.py")

    async def test_default_no_tests(self):
        runner = PytestRunner(bound=">0.8", no_tests_score=0, target="./")
        # TODO fix
        with self.base:  # type: ignore
            with self.assertRaises(RuntimeError) as e:
                await runner.run(
                    target="./",
                    executor=self.base,  # type: ignore
                    env_name=self.env_name,  # type: ignore
                )
            self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_default_empty_tests(self):
        runner = PytestRunner(bound=">0.8", no_tests_score=0, target="./")
        with open(TEST_FILE_PATH, "w") as f:
            f.write(
                """
import pytest
            """
            )
        #     TODO fix
        with self.base:  # type: ignore
            with self.assertRaises(RuntimeError) as e:
                await runner.run(
                    target="./",
                    executor=self.base,  # type: ignore
                    env_name=self.env_name,  # type: ignore
                )
            self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_only_one_test_that_passes(self):
        runner = PytestRunner(bound=">0.8", no_tests_score=0, target="./")
        with open(TEST_FILE_PATH, "w") as f:
            f.write(
                """
import pytest
        
def test_add():
    assert 1 + 1 == 2        
                    """
            )
        with self.base:  # type: ignore
            await runner.run(
                target="./",
                executor=self.base,  # type: ignore
                env_name=self.env_name,  # type: ignore
            )

    async def test_only_one_test_that_fails(self):
        runner = PytestRunner(bound=">0.8", no_tests_score=0, target="./")
        with open(TEST_FILE_PATH, "w") as f:
            f.write(
                """
import pytest

def test_add():
    assert 1 + 1 == 1        
                    """
            )
        #     TODO fix
        with self.base:  # type: ignore
            with self.assertRaises(RuntimeError) as e:
                await runner.run(
                    target="./",
                    executor=self.base,  # type: ignore
                    env_name=self.env_name,  # type: ignore
                )
            self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_combined(self):
        runner = PytestRunner(bound=">=0", no_tests_score=0, target="./")
        with open(TEST_FILE_PATH, "w") as f:
            f.write(
                """
import pytest

def test_add():
    assert 1 + 1 == 1  
    
def test_add2():
    assert 1 + 1 == 2        
                            """
            )
        with self.base:  # type: ignore
            await runner.run(
                target="./",
                executor=self.base,  # type: ignore
                env_name=self.env_name,  # type: ignore
            )

    async def test_combined_with_bound_should_fail(self):
        runner = PytestRunner(bound=">0.8", no_tests_score=0, target="./")
        with open(TEST_FILE_PATH, "w") as f:
            f.write(
                """
import pytest

def test_add():
    assert 1 + 1 == 1  
    
def test_add2():
    assert 1 + 1 == 2        
                            """
            )
        #     TODO fix
        with self.base:  # type: ignore
            with self.assertRaises(RuntimeError) as e:
                await runner.run(
                    target="./",
                    executor=self.base,  # type: ignore
                    env_name=self.env_name,  # type: ignore
                )
            self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_combined_with_bound_should_pass(self):
        runner = PytestRunner(bound=">=0.5", no_tests_score=0, target="./")
        with open(TEST_FILE_PATH, "w") as f:
            f.write(
                """
import pytest

def test_add():
    assert 1 + 1 == 1  
    
def test_add2():
    assert 1 + 1 == 2         
                            """
            )
        with self.base:  # type: ignore
            await runner.run(
                target="./",
                executor=self.base,  # type: ignore
                env_name=self.env_name,  # type: ignore
            )


class TestPytestRunnerBuildCommand(AutoCWDTestCase):
    def setUp(self):
        super().setUp()
        create_file("./__init__.py")

    @patch(
        "quickpub.strategies.implementations.quality_assurance_runners.pytest_qa_runner.subprocess.run"
    )
    def test_build_command_uses_xdist_when_available(self, mock_run):
        mock_run.return_value = Mock(returncode=0)
        runner = PytestRunner()

        command = runner._build_command(target="./tests")

        self.assertIn("-n auto", command)
        mock_run.assert_called_once()

    @patch(
        "quickpub.strategies.implementations.quality_assurance_runners.pytest_qa_runner.subprocess.run"
    )
    def test_build_command_skips_xdist_when_missing(self, mock_run):
        mock_run.return_value = Mock(returncode=1)
        runner = PytestRunner()

        command = runner._build_command(target="./tests")

        self.assertNotIn("-n auto", command)
        mock_run.assert_called_once()

    @patch(
        "quickpub.strategies.implementations.quality_assurance_runners.pytest_qa_runner.subprocess.run"
    )
    def test_build_command_respects_configured_workers(self, mock_run):
        mock_run.return_value = Mock(returncode=0)
        runner = PytestRunner(xdist_workers=4)

        command = runner._build_command(target="./tests")

        self.assertIn("-n 4", command)
        mock_run.assert_called_once()
