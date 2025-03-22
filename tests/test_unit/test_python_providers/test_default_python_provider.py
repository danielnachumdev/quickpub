import sys

from danielutils import get_python_version, AsyncAutoCWDTestCase

from quickpub import DefaultPythonProvider


class TestDefaultPythonProvider(AsyncAutoCWDTestCase):
    async def test_correct_version(self):
        async for x in DefaultPythonProvider():
            name, extr = x
            break
        with extr:
            code, out, err = await extr.execute(f"{sys.executable} --version")
            self.assertEqual(0, code)
            self.assertListEqual([], err)
            out = out[0].strip().split(' ')[1].split('.')
            out = tuple([int(i) for i in out])
            self.assertEqual(get_python_version(), out)
