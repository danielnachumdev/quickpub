import sys
import unittest

from danielutils import get_python_version

from quickpub import DefaultPythonProvider


class TestDefaultPythonProvider(unittest.TestCase):
    def test_correct_version(self):
        name, extr = next(iter(DefaultPythonProvider()))
        with extr:
            code, out, err = extr.execute(f"{sys.executable} --version")
            self.assertEqual(0, code)
            self.assertListEqual([], err)
            out = out[0].strip().split(' ')[1].split('.')
            out = tuple([int(i) for i in out])
            self.assertEqual(get_python_version(), out)
