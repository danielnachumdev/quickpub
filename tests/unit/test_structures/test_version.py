import random
import unittest

from quickpub import Version


class TestVersion(unittest.TestCase):
    def test_from_string__equality(self) -> None:
        for _ in range(10000):
            major, minor, patch = (
                random.randint(1, 100000),
                random.randint(1, 100000),
                random.randint(1, 100000),
            )
            self.assertEqual(
                Version(major, minor, patch),
                Version.from_str(f"{major}.{minor}.{patch}"),
            )

    def test_valid_values(self) -> None:
        Version(0, 0, 0)

    def test_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            Version(",", ",", "")  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            Version(1, ",", "")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            Version(1, 1, "")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            Version(1, ",", 1)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            Version(",", 1, 1)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            Version(",", 1, "")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            Version(",", ",", 1)  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            Version(-1, 0, 0)
        with self.assertRaises(ValueError):
            Version(0, -1, 0)
        with self.assertRaises(ValueError):
            Version(0, 0, -1)

        with self.assertRaises(ValueError):
            Version(0.0, 0, 0)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            Version(0, 0.0, 0)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            Version(0, 0, 0.0)  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            Version(0, 0, -1.0)  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            Version(float("inf"), 0, 1)  # type: ignore[arg-type]
