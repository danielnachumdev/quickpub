import sys

from danielutils import get_python_version

from quickpub import DefaultPythonProvider

from tests.base_test_classes import AsyncBaseTestClass
from tests.test_helpers import temporary_test_directory


class TestDefaultPythonProvider(AsyncBaseTestClass):
    async def test_correct_version(self) -> None:
        with temporary_test_directory():
            async for x in DefaultPythonProvider():
                name, extr = x
                break
            with extr:
                code, out, err = await extr.execute(f"{sys.executable} --version")
                self.assertEqual(0, code)
                self.assertListEqual([], err)
                version_parts = out[0].strip().split(" ")[1].split(".")
                version_tuple = tuple([int(i) for i in version_parts])
                self.assertEqual(get_python_version(), version_tuple)
