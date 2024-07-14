import unittest
from danielutils import frange

from quickpub import Bound


class TestBound(unittest.TestCase):
    def test_from_string(self):
        for f in frange(-5, 5, 0.3654):
            self.assertEqual(Bound(">", f), Bound.from_string(f">{f}"))
            self.assertEqual(Bound(">=", f), Bound.from_string(f">={f}"))
            self.assertEqual(Bound("<", f), Bound.from_string(f"<{f}"))
            self.assertEqual(Bound("<=", f), Bound.from_string(f"<={f}"))
