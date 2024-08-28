import unittest
from quickpub import Version


class TestVersionStructure(unittest.TestCase):
    def setUp(self):
        pass

    def test_from_string(self):
        for i, j, k in zip(range(10), range(10), range(10)):
            s = f"{i}.{j}.{k}"
            v = Version(i, j, k)
            self.assertEqual(v, Version.from_str(s))
            self.assertEqual(str(v), s)

    def test_negative(self):
        with self.assertRaises(ValueError):
            Version(-1)

    def test_fractional(self):
        with self.assertRaises(ValueError):
            Version(0.5)
        with self.assertRaises(ValueError):
            Version(-0.5)
