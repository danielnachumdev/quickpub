import os
from danielutils import create_file, AutoCWDTestCase

from quickpub import DefaultInterpreterProvider, PytestRunner


class TestPytestRunner(AutoCWDTestCase):
    @classmethod
    def setUpClass(cls):
        cls.env_name, cls.base = next(iter(DefaultInterpreterProvider()))  # type: ignore

    def setUp(self):
        create_file("./__init__.py")

    def test_default_no_tests(self):
        runner = PytestRunner(
            bound=">0.8",
            no_tests_score=0,
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

    def test_default_empty_tests(self):
        runner = PytestRunner(
            bound=">0.8",
            no_tests_score=0,
            target="./"
        )
        with open(os.path.join("./", "test_foo.py"), "w") as f:
            f.write("""
import pytest
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
