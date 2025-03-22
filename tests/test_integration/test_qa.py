import os
import unittest
from danielutils import create_file, create_directory, AutoCWDTestCase

from quickpub import CondaPythonProvider, ExitEarlyError
from quickpub.qa import qa

PACKAGE_NAME: str = "foo"


class TestCondaPythonProvider(unittest.IsolatedAsyncioTestCase, AutoCWDTestCase):

    async def asyncSetUp(self):
        create_directory(PACKAGE_NAME)
        create_file(os.path.join(PACKAGE_NAME, "__init__.py"))

    async def test_simplest_case_should_succeed(self) -> None:
        await qa(
            python_provider=CondaPythonProvider(["base"]),
            quality_assurance_strategies=[],
            package_name=PACKAGE_NAME,
            src_folder_path=f"./{PACKAGE_NAME}",
            dependencies=[]
        )

    async def test_wrong_src_folder_path_should_fail(self) -> None:
        await qa(
            python_provider=CondaPythonProvider(["base"]),
            quality_assurance_strategies=[],
            package_name=PACKAGE_NAME,
            src_folder_path="./akjsbgfakjgbakls",
            dependencies=[]
        )

    async def test_non_existing_env_should_skip(self):
        NON_EXISTENT_ENV_NAME: str = "sdjbnglksjdgnwkerjg"
        with self.assertRaises(ExitEarlyError):
            async for x in CondaPythonProvider([NON_EXISTENT_ENV_NAME]):
                pass
