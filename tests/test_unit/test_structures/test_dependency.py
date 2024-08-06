import unittest
from quickpub import Dependency, Version
from danielutils import RandomDataGenerator
import random


class TestBound(unittest.TestCase):
    def test_From_string__equality(self):
        for op in ["<", "<=", "==", "<=", "<"]:
            for _ in range(1000):
                name = RandomDataGenerator.name(10)
                major, minor, patch = random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)
                self.assertEqual(
                    Dependency(
                        name,
                        op,  # type:ignore
                        Version.from_str(f"{major}.{minor}.{patch}")
                    ),
                    Dependency.from_string(f"{name}{op}{major}.{minor}.{patch}"))

    def test_is_satisfied_by(self):
        for _ in range(1000):
            name = RandomDataGenerator.name(10)
            major, minor, patch = random.randint(1, 100), random.randint(1, 100), random.randint(1, 100)
            d = Dependency.from_string(f"{name}>={major}.{minor}.{patch}")
            self.assertTrue(d.is_satisfied_by(Version.from_str(f"{major}.{minor}.{patch + 1}")))
            self.assertTrue(d.is_satisfied_by(Version.from_str(f"{major}.{minor + 1}.{patch}")))
            self.assertTrue(d.is_satisfied_by(Version.from_str(f"{major + 1}.{minor}.{patch}")))
            self.assertFalse(d.is_satisfied_by(Version.from_str(f"{major}.{minor}.{patch - 1}")))
            self.assertFalse(d.is_satisfied_by(Version.from_str(f"{major}.{minor - 1}.{patch}")))
            self.assertFalse(d.is_satisfied_by(Version.from_str(f"{major - 1}.{minor}.{patch}")))
