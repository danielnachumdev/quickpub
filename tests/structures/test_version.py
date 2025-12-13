import unittest
from quickpub import Version


class TestVersionStructure(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_from_string(self) -> None:
        for i, j, k in zip(range(10), range(10), range(10)):
            s = f"{i}.{j}.{k}"
            v = Version(i, j, k)
            self.assertEqual(v, Version.from_str(s))
            self.assertEqual(str(v), s)

    def test_negative(self) -> None:
        with self.assertRaises(ValueError):
            Version(-1)

    def test_fractional(self) -> None:
        with self.assertRaises(ValueError):
            Version(0.5)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            Version(-0.5)  # type: ignore[arg-type]
