import os

from danielutils import AutoCWDTestCase, create_file

from quickpub import UnittestRunner, DefaultPythonProvider

TEST_FILE_PATH: str = "./test_foo.py"


class TestUnittestRunner(AutoCWDTestCase):
    @classmethod
    def setUpClass(cls):
        cls.env_name, cls.base = next(iter(DefaultPythonProvider()))  # type: ignore
        cls.base._instance_flush_stdout = False
        cls.base._instance_flush_stderr = False

    def setUp(self):
        create_file("./__init__.py")

    def test_default_no_tests(self):
        runner = UnittestRunner(
            bound=">0.8",
            target="./"
        )
        with self.assertRaises(SystemExit):
            with self.base:  # type: ignore
                runner.run(
                    target="./",
                    executor=self.base,  # type: ignore
                    print_func=print,
                    env_name=self.env_name  # type: ignore
                )
        runner.no_tests_score = 1
        with self.base:  # type: ignore
            runner.run(
                target="./",
                executor=self.base,  # type: ignore
                print_func=print,
                env_name=self.env_name  # type: ignore
            )

    def test_default_empty_tests(self):
        runner = UnittestRunner(
            bound=">0.8",
            target="./"
        )
        with open(TEST_FILE_PATH, "w") as f:
            f.write("""
import unittest

class TestFoo(unittest.TestCase):
    pass
                """)
        with self.assertRaises(SystemExit):
            with self.base:  # type: ignore
                runner.run(
                    target="./",
                    executor=self.base,  # type: ignore
                    print_func=print,
                    env_name=self.env_name  # type: ignore
                )

    def test_only_one_test_that_passes(self):
        runner = UnittestRunner(
            bound=">0.8",
            target="./"
        )
        with open(TEST_FILE_PATH, "w") as f:
            f.write("""
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 2        
                        """)
        with self.base:  # type: ignore
            runner.run(
                target="./",
                executor=self.base,  # type: ignore
                print_func=print,
                env_name=self.env_name  # type: ignore
            )

    def test_only_one_test_that_fails(self):
        runner = UnittestRunner(
            bound=">0.8",
            target="./"
        )
        with open(TEST_FILE_PATH, "w") as f:
            f.write("""
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 1       
                        """)
        with self.assertRaises(SystemExit):
            with self.base:  # type: ignore
                runner.run(
                    target="./",
                    executor=self.base,  # type: ignore
                    print_func=print,
                    env_name=self.env_name  # type: ignore
                )

    def test_combined(self):
        runner = UnittestRunner(
            bound=">=0",
            target="./"
        )
        with open(TEST_FILE_PATH, "w") as f:
            f.write("""
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 2     
        
    def test_add2(self):
        assert 1 + 1 == 1    
                                """)
        with self.base:  # type: ignore
            runner.run(
                target="./",
                executor=self.base,  # type: ignore
                print_func=print,
                env_name=self.env_name  # type: ignore
            )

    def test_combined_with_bound_should_fail(self):
        runner = UnittestRunner(
            bound=">0.8",
            no_tests_score=0,
            target="./"
        )
        with open(TEST_FILE_PATH, "w") as f:
            f.write("""
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 2     
        
    def test_add2(self):
        assert 1 + 1 == 1    
                                """)
        with self.assertRaises(SystemExit):
            with self.base:  # type: ignore
                runner.run(
                    target="./",
                    executor=self.base,  # type: ignore
                    print_func=print,
                    env_name=self.env_name  # type: ignore
                )

    def test_combined_with_bound_should_pass(self):
        runner = UnittestRunner(
            bound=">=0.5",
            no_tests_score=0,
            target="./"
        )
        with open(TEST_FILE_PATH, "w") as f:
            f.write("""
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 2     
        
    def test_add2(self):
        assert 1 + 1 == 1    
                                """)
        with self.base:  # type: ignore
            runner.run(
                target="./",
                executor=self.base,  # type: ignore
                print_func=print,
                env_name=self.env_name  # type: ignore
            )

    def test_failure_and_error(self):
        runner = UnittestRunner(
            bound=">=0.01",
            no_tests_score=0,
            target="./"
        )
        with open(TEST_FILE_PATH, "w") as f:
            f.write("""
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 1     

    def test_add2():
        assert 1 + 1 == 1    
                                """)
        with self.assertRaises(SystemExit):
            with self.base:  # type: ignore
                runner.run(
                    target="./",
                    executor=self.base,  # type: ignore
                    print_func=print,
                    env_name=self.env_name  # type: ignore
                )

    def test_failure_and_error_and_success(self):
        runner = UnittestRunner(
            bound=">=0.333333",
            no_tests_score=0,
            target="./"
        )
        with open(TEST_FILE_PATH, "w") as f:
            f.write("""
import unittest

class TestFoo(unittest.TestCase):

    def test_add(self):
        assert 1 + 1 == 1     

    def test_add2():
        assert 1 + 1 == 1
           
    def test_add3(self):
        assert 1 + 1 == 2  
                                """)
        with self.base:  # type: ignore
            runner.run(
                target="./",
                executor=self.base,  # type: ignore
                print_func=print,
                env_name=self.env_name  # type: ignore
            )
