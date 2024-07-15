import unittest

from utils import improved_setup, improved_teardown, AutoCWDTestCase


class TestLocalVersionEnforcer(AutoCWDTestCase):
    def test_no_dist_folder_should_pass(self) -> None:
        pass

    def test_empty_dist_folder_should_pass(self) -> None:
        pass

    def test_should_pass(self) -> None:
        pass

    def test_should_fail(self) -> None:
        pass
