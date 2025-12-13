import os
import unittest

from quickpub import UnittestRunner, DefaultPythonProvider, ExitEarlyError

from tests.base_test_classes import AsyncBaseTestClass
from tests.test_helpers import temporary_test_directory

TEST_FILE_PATH: str = "test_foo.py"


class TestUnittestRunner(AsyncBaseTestClass):
    async def _setup_provider(self):
        """Helper method to set up the Python provider."""
        async for name, base in DefaultPythonProvider():
            base.prev = None
            return name, base
        raise RuntimeError("No Python provider found")

    async def test_default_no_tests(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = UnittestRunner(bound=">0.8", target=str(tmp_dir))
            with base:  # type: ignore
                with self.assertRaises(RuntimeError) as e:
                    await runner.run(
                        target=str(tmp_dir),
                        executor=base,  # type: ignore
                        env_name=env_name,  # type: ignore
                    )
                self.assertIsInstance(e.exception.__cause__, ExitEarlyError)
            runner.no_tests_score = 1
            with base:  # type: ignore
                await runner.run(
                    target=str(tmp_dir),
                    executor=base,  # type: ignore
                    env_name=env_name,  # type: ignore
                )

    async def test_default_empty_tests(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import unittest

class TestFoo(unittest.TestCase):
    pass
                """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = UnittestRunner(bound=">0.8", target=str(tmp_dir))
            with base:  # type: ignore
                with self.assertRaises(RuntimeError) as e:
                    await runner.run(
                        target=str(tmp_dir),
                        executor=base,  # type: ignore
                        env_name=env_name,  # type: ignore
                    )
                self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_only_one_test_that_passes(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 2        
                        """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = UnittestRunner(bound=">0.8", target=str(tmp_dir))
            with base:  # type: ignore
                await runner.run(
                    target=str(tmp_dir),
                    executor=base,  # type: ignore
                    env_name=env_name,  # type: ignore
                )

    async def test_only_one_test_that_fails(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 1       
                        """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = UnittestRunner(bound=">0.8", target=str(tmp_dir))
            with base:  # type: ignore
                with self.assertRaises(RuntimeError) as e:
                    await runner.run(
                        target=str(tmp_dir),
                        executor=base,  # type: ignore
                        env_name=env_name,  # type: ignore
                    )
                self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_combined(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 2     
        
    def test_add2(self):
        assert 1 + 1 == 1    
                                """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = UnittestRunner(bound=">=0", target=str(tmp_dir))
            with base:  # type: ignore
                await runner.run(
                    target=str(tmp_dir),
                    executor=base,  # type: ignore
                    env_name=env_name,  # type: ignore
                )

    async def test_combined_with_bound_should_fail(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 2     
        
    def test_add2(self):
        assert 1 + 1 == 1    
                                """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = UnittestRunner(bound=">0.8", no_tests_score=0, target=str(tmp_dir))
            with base:  # type: ignore
                with self.assertRaises(RuntimeError) as e:
                    await runner.run(
                        target=str(tmp_dir),
                        executor=base,  # type: ignore
                        env_name=env_name,  # type: ignore
                    )
                self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_combined_with_bound_should_pass(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 2     
        
    def test_add2(self):
        assert 1 + 1 == 1    
                                """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = UnittestRunner(
                bound=">=0.5", no_tests_score=0, target=str(tmp_dir)
            )
            with base:  # type: ignore
                await runner.run(
                    target=str(tmp_dir),
                    executor=base,  # type: ignore
                    env_name=env_name,  # type: ignore
                )

    async def test_failure_and_error(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 1     

    def test_add2():
        assert 1 + 1 == 1    
                                """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = UnittestRunner(
                bound=">=0.01", no_tests_score=0, target=str(tmp_dir)
            )
            with base:  # type: ignore
                with self.assertRaises(RuntimeError) as e:
                    await runner.run(
                        target=str(tmp_dir),
                        executor=base,  # type: ignore
                        env_name=env_name,  # type: ignore
                    )
                self.assertIsInstance(e.exception.__cause__, ExitEarlyError)

    async def test_failure_and_error_and_success(self):
        with temporary_test_directory() as tmp_dir:
            (tmp_dir / "__init__.py").touch()
            test_file = tmp_dir / TEST_FILE_PATH
            test_file.write_text(
                """
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 1     

    def test_add2():
        assert 1 + 1 == 1
           
    def test_add3(self):
        assert 1 + 1 == 2  
                                """
            )
            env_name, base = await self._setup_provider()
            base._instance_flush_stdout = False
            base._instance_flush_stderr = False
            runner = UnittestRunner(
                bound=">=0.333333", no_tests_score=0, target=str(tmp_dir)
            )
            with base:  # type: ignore
                await runner.run(
                    target=str(tmp_dir),
                    executor=base,  # type: ignore
                    env_name=env_name,  # type: ignore
                )
