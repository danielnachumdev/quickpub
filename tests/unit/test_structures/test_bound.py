import unittest
from danielutils import frange

from quickpub import Bound


class TestBound(unittest.TestCase):
    def test_from_string__equality(self) -> None:
        for f in frange(-5, 5, 0.3654):
            self.assertEqual(Bound(">", f), Bound.from_string(f">{f}"))
            self.assertEqual(Bound(">=", f), Bound.from_string(f">={f}"))
            self.assertEqual(Bound("<", f), Bound.from_string(f"<{f}"))
            self.assertEqual(Bound("<=", f), Bound.from_string(f"<={f}"))

    def test_from_string_invalid_inputs(self) -> None:
        with self.assertRaises(ValueError):
            Bound.from_string(">")
        with self.assertRaises(ValueError):
            Bound.from_string(">=")
        with self.assertRaises(ValueError):
            Bound.from_string("==")
        with self.assertRaises(ValueError):
            Bound.from_string("<")
        with self.assertRaises(ValueError):
            Bound.from_string("<=")

        with self.assertRaises(ValueError):
            Bound.from_string("124")

        with self.assertRaises(ValueError):
            Bound.from_string("?35")

    def test_compare_against(self) -> None:
        self.assertTrue(Bound.from_string("<1").compare_against(-float("inf")))
        self.assertTrue(Bound.from_string("<1").compare_against(0))
        self.assertTrue(Bound.from_string("<1").compare_against(-1))
        self.assertFalse(Bound.from_string("<1").compare_against(1))
        self.assertFalse(Bound.from_string("<1").compare_against(2))
        self.assertFalse(Bound.from_string("<1").compare_against(float("inf")))
