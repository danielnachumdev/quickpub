import unittest
from quickpub import Dependency, Version


class TestBound(unittest.TestCase):
    def test_From_string__equality(self):
        self.assertEqual(Dependency("foo", "<", Version.from_str("1.0.0")), Dependency.from_string("foo<1.0.0"))

    def test_is_satisfied_by(self):
        pass
