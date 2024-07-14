import os
import unittest
from danielutils import create_directory, delete_directory, create_file

from quickpub import DefaultInterpreterProvider, PytestRunner

TESTS_FOLDER_NAME: str = "./tmp_pytest_tests_folder"


class TestPytestRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env_name, cls.base = next(iter(DefaultInterpreterProvider()))  # type: ignore

    def setUp(self):
        create_directory(TESTS_FOLDER_NAME)
        create_file(os.path.join(TESTS_FOLDER_NAME, "__init__.py"))

    def tearDown(self):
        delete_directory(TESTS_FOLDER_NAME)

    def test_default_no_tests(self):
        runner = PytestRunner(
            bound=">0.8",
            no_tests_score=0,
            target=TESTS_FOLDER_NAME
        )
        with self.assertRaises(SystemExit):
            with self.base:  # type: ignore
                runner.run(
                    target=TESTS_FOLDER_NAME,
                    executor=self.base,  # type: ignore
                    print_func=print,
                    env_name=self.env_name  # type: ignore
                )

    def test_default_empty_tests(self):
        runner = PytestRunner(
            bound=">0.8",
            no_tests_score=0,
            target=TESTS_FOLDER_NAME
        )
        with open(os.path.join(TESTS_FOLDER_NAME, "test_foo.py"), "w") as f:
            f.write("""
import pytest
            """)
        with self.assertRaises(SystemExit):
            with self.base:  # type: ignore
                runner.run(
                    target=TESTS_FOLDER_NAME,
                    executor=self.base,  # type: ignore
                    print_func=print,
                    env_name=self.env_name  # type: ignore
                )

    def test_only_one_test_that_passes(self):
        # TODO
        pass

    def test_only_one_test_that_fails(self):
        # TODO
        pass

    def test_combined(self):
        # TODO
        pass

    def test_combined_with_bound_should_fail(self):
        # TODO
        pass

    def test_combined_with_bound_should_pass(self):
        # TODO
        pass
